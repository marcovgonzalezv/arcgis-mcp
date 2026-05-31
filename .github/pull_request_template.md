## Summary

- Describe the change.

## Validation

- [ ] `.\scripts\validate_release.ps1`
- [ ] `python -m ruff check . --no-cache`
- [ ] `python -m ruff format . --check --no-cache`
- [ ] `python -m pytest -q`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `dotnet build .\ArcGisMcpAddin.sln`

## ArcGIS Pro validation

- [ ] Add-In installed in ArcGIS Pro 3.7
- [ ] `python test_connection.py`
- [ ] `health_check`
- [ ] `get_capabilities`
