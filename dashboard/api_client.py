import requests
from typing import Optional, Dict, Any, List

class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text}

        if response.status_code >= 400:
            error_msg = data.get("detail", f"Request failed with status {response.status_code}")
            if isinstance(error_msg, list):
                error_msg = "\n".join(str(m) for m in error_msg)
            elif isinstance(error_msg, dict):
                error_msg = str(error_msg)
            raise Exception(error_msg)

        return data

    # 1. Auth APIs
    def login(self, email: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/login"
        resp = self.session.post(url, json={"email": email, "password": password})
        return self._handle_response(resp)

    def register(
        self,
        full_name: str,
        email: str,
        password: str,
        role: str,
        admin_secret: Optional[str] = None,
        phone: Optional[str] = None,
        business_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/register"
        payload = {
            "full_name": full_name,
            "email": email,
            "password": password,
            "role": role
        }
        if admin_secret:
            payload["admin_secret"] = admin_secret
        if phone:
            payload["phone"] = phone
        if business_name:
            payload["business_name"] = business_name
        if category:
            payload["category"] = category
        resp = self.session.post(url, json=payload)
        return self._handle_response(resp)

    def reset_password(self, email: str, new_password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/reset-password"
        resp = self.session.post(url, json={"email": email, "new_password": new_password})
        return self._handle_response(resp)

    def get_me(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/me"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    # 2. Analytics APIs
    def get_summary(self, token: str, vendor_id: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/analytics/summary"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_vendor_performance(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/vendor-performance"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_product_performance(self, token: str, vendor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/product-performance"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_revenue_trend(self, token: str, vendor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/revenue-trend"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_category_performance(self, token: str, vendor_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/category-performance"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    # 2b. Milestone 2 Customer Analytics & Segmentation
    def get_customer_behavior(self, token: str, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/analytics/customers"
        params = {}
        if customer_id:
            params["customer_id"] = customer_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_customer_segments(self, token: str, n_clusters: int = 3) -> Dict[str, Any]:
        url = f"{self.base_url}/api/analytics/segments"
        params = {"n_clusters": n_clusters}
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    # 3. Vendor APIs
    def get_vendors(
        self,
        token: str,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        application_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/vendors"
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        if status and status != "All":
            params["status"] = status
        if application_status and application_status != "All":
            params["application_status"] = application_status
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def review_vendor_application(self, token: str, vendor_id: int, action: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Admin review of vendor application: APPROVE, REQUEST_INFO, or REJECT."""
        url = f"{self.base_url}/api/vendors/{vendor_id}/review"
        resp = self.session.post(url, headers=self._headers(token), json={"action": action, "notes": notes})
        return self._handle_response(resp)

    def create_vendor(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/vendors"
        resp = self.session.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def update_vendor(self, token: str, vendor_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/vendors/{vendor_id}"
        resp = self.session.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def delete_vendor(self, token: str, vendor_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/vendors/{vendor_id}"
        resp = self.session.delete(url, headers=self._headers(token))
        return self._handle_response(resp)

    # 4. Product APIs
    def get_products(
        self,
        token: str,
        vendor_id: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/products"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        if category and category != "All":
            params["category"] = category
        if search:
            params["search"] = search
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def create_product(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products"
        resp = self.session.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def update_product(self, token: str, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products/{product_id}"
        resp = self.session.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def delete_product(self, token: str, product_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products/{product_id}"
        resp = self.session.delete(url, headers=self._headers(token))
        return self._handle_response(resp)

    # 5. Inventory APIs
    def get_inventory(self, token: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/inventory"
        params = {}
        if status and status != "All":
            params["status"] = status
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def update_inventory(self, token: str, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/inventory/{product_id}"
        resp = self.session.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def get_inventory_alerts(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/inventory/alerts"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_inventory_turnover(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/inventory/turnover"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_inventory_forecast(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/inventory/forecast"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_replenishment_recommendations(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/inventory/replenishment"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_stock_movements(self, token: str, product_id: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/inventory/movements"
        params = {}
        if product_id:
            params["product_id"] = product_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def record_stock_movement(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/inventory/movements"
        resp = self.session.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    # 6. Warehouse APIs
    def get_warehouses(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/warehouses"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def create_warehouse(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/warehouses"
        resp = self.session.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def update_warehouse(self, token: str, warehouse_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/warehouses/{warehouse_id}"
        resp = self.session.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    # 7. Category APIs
    def get_categories(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/categories"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_category_tree(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/categories/tree"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def create_category(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/categories"
        resp = self.session.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    def update_category(self, token: str, category_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/categories/{category_id}"
        resp = self.session.put(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    # 8. Recommendation APIs
    def get_recommendations(self, token: str, customer_id: int, top_n: int = 5) -> Dict[str, Any]:
        url = f"{self.base_url}/api/recommendations/{customer_id}"
        params = {"top_n": top_n}
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_recommendation_evaluation(self, token: str, k: int = 5) -> Dict[str, Any]:
        url = f"{self.base_url}/api/recommendations/evaluation"
        params = {"k": k}
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    # 9. Transaction APIs
    def get_transactions(
        self,
        token: str,
        vendor_id: Optional[int] = None,
        product_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/transactions"
        params = {}
        if vendor_id:
            params["vendor_id"] = vendor_id
        if product_id:
            params["product_id"] = product_id
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def create_transaction(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/transactions"
        resp = self.session.post(url, headers=self._headers(token), json=data)
        return self._handle_response(resp)

    # 10. Milestone 3 Analytics & Reporting APIs
    def get_advanced_revenue(self, token: str, vendor_id: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/revenue"
        params = {"vendor_id": vendor_id} if vendor_id else {}
        resp = self.session.get(url, headers=self._headers(token), params=params)
        return self._handle_response(resp)

    def get_registered_models(self, token: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/models"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_workflow_stats(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/workflows/stats"
        resp = self.session.get(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_workflow_history(self, token: str, limit: int = 25) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/workflows/history"
        resp = self.session.get(url, headers=self._headers(token), params={"limit": limit})
        return self._handle_response(resp)

    def trigger_workflow_run(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/workflows/run"
        resp = self.session.post(url, headers=self._headers(token))
        return self._handle_response(resp)

    def run_consistency_validation(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/validation/run"
        resp = self.session.post(url, headers=self._headers(token))
        return self._handle_response(resp)

    def get_validation_history(self, token: str, limit: int = 10) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/validation/history"
        resp = self.session.get(url, headers=self._headers(token), params={"limit": limit})
        return self._handle_response(resp)

    def run_performance_benchmarks(self, token: str, iterations: int = 5) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/performance/run"
        resp = self.session.post(url, headers=self._headers(token), params={"iterations": iterations})
        return self._handle_response(resp)

    def get_performance_history(self, token: str, limit: int = 25) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/performance/history"
        resp = self.session.get(url, headers=self._headers(token), params={"limit": limit})
        return self._handle_response(resp)

    def download_excel_report_bytes(self, token: str, vendor_id: Optional[int] = None) -> bytes:
        url = f"{self.base_url}/analytics/reports/excel"
        params = {"vendor_id": vendor_id} if vendor_id else {}
        resp = self.session.get(url, headers=self._headers(token), params=params)
        if resp.status_code == 200:
            return resp.content
        raise Exception(f"Failed to download Excel report: {resp.text}")

    def download_pdf_report_bytes(self, token: str, vendor_id: Optional[int] = None) -> bytes:
        url = f"{self.base_url}/analytics/reports/pdf"
        params = {"vendor_id": vendor_id} if vendor_id else {}
        resp = self.session.get(url, headers=self._headers(token), params=params)
        if resp.status_code == 200:
            return resp.content
        raise Exception(f"Failed to download PDF report: {resp.text}")


    # Profile & Address Management APIs
    def get_vendor_profile(self, token: str) -> Dict[str, Any]:
        res = requests.get(f"{self.base_url}/api/vendor/profile", headers=self._headers(token))
        return self._handle_response(res)

    def update_vendor_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.put(f"{self.base_url}/api/vendor/profile", json=data, headers=self._headers(token))
        return self._handle_response(res)

    def get_customer_profile(self, token: str) -> Dict[str, Any]:
        res = requests.get(f"{self.base_url}/api/customer/profile", headers=self._headers(token))
        return self._handle_response(res)

    def update_customer_profile(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.put(f"{self.base_url}/api/customer/profile", json=data, headers=self._headers(token))
        return self._handle_response(res)

    def get_addresses(self, token: str) -> List[Dict[str, Any]]:
        res = requests.get(f"{self.base_url}/api/addresses", headers=self._headers(token))
        return self._handle_response(res)

    def create_address(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.post(f"{self.base_url}/api/addresses", json=data, headers=self._headers(token))
        return self._handle_response(res)

    def update_address(self, token: str, address_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.put(f"{self.base_url}/api/addresses/{address_id}", json=data, headers=self._headers(token))
        return self._handle_response(res)

    def set_default_address(self, token: str, address_id: int) -> Dict[str, Any]:
        res = requests.put(f"{self.base_url}/api/addresses/{address_id}/default", headers=self._headers(token))
        return self._handle_response(res)

    def delete_address(self, token: str, address_id: int) -> Dict[str, Any]:
        res = requests.delete(f"{self.base_url}/api/addresses/{address_id}", headers=self._headers(token))
        return self._handle_response(res)
