import pytest
from unittest.mock import Mock
from app.domain.services.user_service import UserService
from app.domain.entities.user import User

def test_get_user_info_for_display_found():
    # Setup
    user_repo = Mock()
    user_repo.find_user_by_card_number.return_value = User(
        id=1, name="Juan", last_name="Perez", numero_tarjeta=123
    )
    
    # Pass mocks for other repos as they are not used in this method
    service = UserService(user_repo, Mock(), Mock())
    
    # Act
    info = service.get_user_info_for_display(123)
    
    # Assert
    assert info['name'] == "Juan Perez"
    assert info['id'] == 1
    user_repo.find_user_by_card_number.assert_called_once_with(123)

def test_get_user_info_for_display_not_found():
    user_repo = Mock()
    user_repo.find_user_by_card_number.return_value = None
    service = UserService(user_repo, Mock(), Mock())
    
    info = service.get_user_info_for_display(999)
    assert info['name'] == 'Usuario aún no registrado'
    assert info['id'] is None
