import pytest

after_signin = pytest.mark.order(after=["test_auth.py::test_signin"])
wait_get_all_active_payment_method = pytest.mark.order(
    after=["test_payment.py::test_get_all_active_payment_method"]
)
