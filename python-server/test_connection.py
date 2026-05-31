from pipe_client import ArcGisPipeClient


def test_connection():
    print("====================================================")
    print("Testing Named Pipe connection to ArcGIS Pro Add-In...")
    print("====================================================")

    client = ArcGisPipeClient()
    try:
        response = client.send_command("ping", timeout_ms=2500)
        if response.get("success"):
            data = response.get("data", {})
            print("SUCCESS: Connected to ArcGIS Pro MCP Bridge.")
            print(f"Response message: {data.get('message')}")
            print(f"ArcGIS Pro Time: {data.get('time')}")
            print("====================================================")
            return True

        print("FAILED: Server returned an error:")
        print(response.get("error"))
        return False
    except TimeoutError as exc:
        print("CONNECTION TIMEOUT:")
        print(exc)
        print("\nTroubleshooting steps:")
        print("1. Verify ArcGIS Pro 3.7 is open and running.")
        print("2. Verify that the C# Add-In was compiled successfully.")
        print("3. Verify that ArcGisMcpAddin.esriAddinX is installed in:")
        print("   %USERPROFILE%\\Documents\\ArcGIS\\AddIns\\ArcGISPro\\")
        print("4. Close and reopen ArcGIS Pro after installing the Add-In package.")
        print("====================================================")
        return False
    except OSError as exc:
        print("IPC ERROR:")
        print(exc)
        if (
            "Code 5" in str(exc)
            or "Access is denied" in str(exc)
            or "Acceso denegado" in str(exc)
        ):
            print("\nAccess denied troubleshooting:")
            print("1. Run ArcGIS Pro and Python at the same permission level.")
            print(
                "2. If ArcGIS Pro was started as administrator, run this test as administrator too."
            )
            print(
                "3. Prefer closing ArcGIS Pro and reopening it normally, then rerun this test normally."
            )
        print("====================================================")
        return False
    except ValueError as exc:
        print("INVALID RESPONSE:")
        print(exc)
        print("====================================================")
        return False


if __name__ == "__main__":
    test_connection()
