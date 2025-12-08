import time
from unittest.mock import patch

from src.main import hello_world, expensive_db_calculation, get_product_with_cache


class TestExpensiveDbCalculation:
    """Tests for expensive_db_calculation function"""

    def test_expensive_db_calculation_returns_list(self):
        result = expensive_db_calculation(1111)
        assert isinstance(result, list)

    def test_expensive_db_calculation_returns_correct_structure(self):
        user_id = 1111
        result = expensive_db_calculation(user_id)

        assert len(result) == 2
        assert "product" in result[0]
        assert "cashflow" in result[0]
        assert "total" in result[0]
        assert result[0]["product"] == "DECUMULATOR"
        assert result[0]["cashflow"] == 1213213
        assert result[0]["total"] == 122132131

        assert "product" in result[1]
        assert "total2" in result[1]
        assert result[1]["product"] == "ACCUMULATOR"
        assert result[1]["total2"] == 2132131

    def test_expensive_db_calculation_takes_time(self):
        start_time = time.time()
        expensive_db_calculation(1111)
        end_time = time.time()

        elapsed_time = end_time - start_time
        assert elapsed_time >= 1.0


class TestGetProductWithCache:
    """Tests for the get_product_with_cache function"""

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_cache_miss_calls_db_and_sets_cache(self, mock_db_calc, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True

        expected_data = [{"product": "TEST", "total": 123}]
        mock_db_calc.return_value = expected_data

        result = get_product_with_cache(1111)

        mock_cache.get.assert_called_once_with("account_value:1111")
        mock_db_calc.assert_called_once_with(1111)
        mock_cache.set.assert_called_once_with("account_value:1111", expected_data, 120)
        assert result == expected_data

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_cache_hit_does_not_call_db(self, mock_db_calc, mock_cache):
        cached_data = [{"product": "CACHED", "total": 999}]
        mock_cache.get.return_value = cached_data

        result = get_product_with_cache(1111)

        mock_cache.get.assert_called_once_with("account_value:1111")
        mock_db_calc.assert_not_called()
        mock_cache.set.assert_not_called()
        assert result == cached_data

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_cache_write_failure_still_returns_data(self, mock_db_calc, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set.return_value = False

        expected_data = [{"product": "TEST", "total": 456}]
        mock_db_calc.return_value = expected_data

        result = get_product_with_cache(1111)

        assert result == expected_data
        mock_db_calc.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_different_user_ids_use_different_cache_keys(self, mock_db_calc, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        mock_db_calc.return_value = [{"product": "TEST"}]

        get_product_with_cache(1111)
        get_product_with_cache(2222)

        assert mock_cache.get.call_count == 2
        mock_cache.get.assert_any_call("account_value:1111")
        mock_cache.get.assert_any_call("account_value:2222")

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_cache_expiration_set_correctly(self, mock_db_calc, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        mock_db_calc.return_value = [{"product": "TEST"}]

        get_product_with_cache(1111)

        call_args = mock_cache.set.call_args
        assert call_args[0][2] == 120

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_cache_key_format(self, mock_db_calc, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        mock_db_calc.return_value = [{"product": "TEST"}]

        user_id = 5555
        get_product_with_cache(user_id)

        expected_key = f"account_value:{user_id}"
        mock_cache.get.assert_called_once_with(expected_key)
        mock_cache.set.assert_called_once()
        assert mock_cache.set.call_args[0][0] == expected_key

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_returns_db_data_structure(self, mock_db_calc, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True

        db_data = [
            {
                "product": "DECUMULATOR",
                "cashflow": 1213213,
                "total": 122132131
            },
            {
                "product": "ACCUMULATOR",
                "total2": 2132131
            }
        ]
        mock_db_calc.return_value = db_data

        result = get_product_with_cache(1111)

        assert result == db_data
        assert len(result) == 2
        assert result[0]["product"] == "DECUMULATOR"
        assert result[1]["product"] == "ACCUMULATOR"


class TestCacheAsidePattern:
    """Integration-style tests for the cache-aside pattern implementation"""

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_cache_aside_pattern_flow(self, mock_db_calc, mock_cache):
        db_data = [{"product": "TEST", "total": 100}]
        mock_db_calc.return_value = db_data

        mock_cache.get.side_effect = [None, db_data]
        mock_cache.set.return_value = True

        result1 = get_product_with_cache(1111)
        assert result1 == db_data
        assert mock_db_calc.call_count == 1

        result2 = get_product_with_cache(1111)
        assert result2 == db_data
        assert mock_db_calc.call_count == 1

    @patch('src.main.CACHE_MANAGER')
    @patch('src.main.expensive_db_calculation')
    def test_multiple_users_independent_cache(self, mock_db_calc, mock_cache):
        user1_data = [{"product": "USER1", "total": 100}]
        user2_data = [{"product": "USER2", "total": 200}]

        def db_side_effect(user_id):
            if user_id == 1111:
                return user1_data
            return user2_data

        mock_db_calc.side_effect = db_side_effect
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True

        result1 = get_product_with_cache(1111)
        result2 = get_product_with_cache(2222)

        assert result1 == user1_data
        assert result2 == user2_data
        assert mock_db_calc.call_count == 2
