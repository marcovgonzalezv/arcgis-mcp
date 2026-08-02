import itertools
import json
import struct
import time
import warnings

import pywintypes
import win32file
import win32pipe

PIPE_NAME = r"\\.\pipe\ArcGisMcpBridge"
DEFAULT_TIMEOUT_MS = 5000
DEFAULT_RETRIES = 2
DEFAULT_RETRY_DELAY_MS = 250


class ArcGisPipeClient:
    _id_counter = itertools.count(1)

    def __init__(
        self,
        pipe_name=PIPE_NAME,
        timeout_ms=DEFAULT_TIMEOUT_MS,
        retries=DEFAULT_RETRIES,
        retry_delay_ms=DEFAULT_RETRY_DELAY_MS,
    ):
        self.pipe_name = pipe_name
        self.timeout_ms = timeout_ms
        self.retries = retries
        self.retry_delay_ms = retry_delay_ms

    def _connect(self, timeout_ms=3000):
        start_time = time.time()
        while True:
            try:
                win32pipe.WaitNamedPipe(self.pipe_name, 1000)

                handle = win32file.CreateFile(
                    self.pipe_name,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None,
                )
                return handle
            except pywintypes.error as e:
                err_code = e.args[0]
                if err_code in (2, 231):
                    if (time.time() - start_time) * 1000 > timeout_ms:
                        raise TimeoutError(
                            f"Connection to ArcGIS Pro pipe timed out after {timeout_ms}ms."
                            " Is ArcGIS Pro running and Add-In loaded?"
                        )
                    time.sleep(0.2)
                    continue
                raise

    @staticmethod
    def _read_exactly(handle, size: int) -> bytes:
        chunks = []
        remaining = size

        while remaining > 0:
            err, chunk = win32file.ReadFile(handle, remaining)
            if err != 0:
                raise OSError(f"Failed to read from ArcGIS Pro pipe. Code: {err}")
            if not chunk:
                raise OSError(
                    "ArcGIS Pro pipe closed before the full response was read."
                )

            chunks.append(chunk)
            remaining -= len(chunk)

        return b"".join(chunks)

    def send_command(
        self, command: str, params: dict = None, timeout_ms=None, retries=None
    ) -> dict:
        timeout = timeout_ms or self.timeout_ms
        attempts = self.retries if retries is None else retries
        started = time.perf_counter()
        last_error = None

        for attempt in range(attempts + 1):
            try:
                response = self._send_once(command, params or {}, timeout)
                response.setdefault("success", False)
                response.setdefault(
                    "elapsed_ms", int((time.perf_counter() - started) * 1000)
                )
                return response
            except (TimeoutError, IOError, OSError, pywintypes.error) as exc:
                last_error = exc
                if attempt >= attempts:
                    break
                time.sleep(self.retry_delay_ms / 1000)

        return {
            "success": False,
            "error_code": "IPC_UNAVAILABLE",
            "message": str(last_error),
            "error": str(last_error),
            "data": None,
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
        }

    def _send_once(self, command: str, params: dict, timeout_ms: int) -> dict:
        request_id = next(self._id_counter)
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "Invoke",
            "params": [command, params],
            "id": request_id,
        }

        request_bytes = json.dumps(rpc_request).encode("utf-8")
        length_prefix = struct.pack("<I", len(request_bytes))

        handle = None
        try:
            handle = self._connect(timeout_ms)

            win32file.WriteFile(handle, length_prefix)
            win32file.WriteFile(handle, request_bytes)

            length_prefix_resp = self._read_exactly(handle, 4)
            resp_length = struct.unpack("<I", length_prefix_resp)[0]

            resp_bytes = self._read_exactly(handle, resp_length)
            rpc_response = json.loads(resp_bytes.decode("utf-8"))

            if "error" in rpc_response:
                err = rpc_response["error"]
                message = err.get("message", str(err))
                return {
                    "success": False,
                    "error_code": str(err.get("code", "RPC_ERROR")),
                    "message": message,
                    "error": message,
                    "data": None,
                    "elapsed_ms": 0,
                }

            return rpc_response.get("result", {})

        except pywintypes.error as e:
            raise IOError(
                f"Windows IPC error communicating with ArcGIS Pro: {e.strerror}"
                f" (Code {e.winerror})"
            ) from e
        finally:
            if handle is not None:
                try:
                    win32file.CloseHandle(handle)
                except pywintypes.error as exc:
                    warnings.warn(
                        f"Failed to close ArcGIS Pro pipe handle: {exc}",
                        ResourceWarning,
                        stacklevel=2,
                    )
