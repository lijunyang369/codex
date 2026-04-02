from unittest import TestCase

from fastapi.testclient import TestClient

from ocr_service.app.main import create_app
from ocr_service.providers.base import OCRProviderError, ProviderHealth


class _FailingService:
    def health(self):
        return ProviderHealth(status="degraded", provider="paddle", detail="down")

    def readiness(self):
        return ProviderHealth(status="degraded", provider="paddle", detail="down")

    def read_text(self, request):
        del request
        raise OCRProviderError("provider failed")

    def read_lines(self, request):
        del request
        raise OCRProviderError("provider failed")


class RoutesTests(TestCase):
    def test_health_is_lightweight(self) -> None:
        app = create_app()
        client = TestClient(app)

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "service is running")

    def test_readiness_uses_service_check(self) -> None:
        from ocr_service.app import routes

        app = create_app()
        app.dependency_overrides[routes.get_ocr_service] = lambda: _FailingService()
        client = TestClient(app)

        response = client.get("/readiness")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "down")

    def test_provider_error_maps_to_502(self) -> None:
        from ocr_service.app import routes

        app = create_app()
        app.dependency_overrides[routes.get_ocr_service] = lambda: _FailingService()
        client = TestClient(app)

        response = client.post("/v1/ocr/read-text", json={"image_base64": "%%%"} )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "provider failed")

    def test_unsupported_profile_maps_to_400(self) -> None:
        app = create_app()
        client = TestClient(app)

        response = client.post(
            "/v1/ocr/read-text",
            json={"image_base64": "Zm9v", "profile": "digits"},
        )

        self.assertEqual(response.status_code, 400)
