from entities.enum.errors_enum import ValidationErrorCodeEnum
from use_cases.auth.authorization_use_case import AuthorizationUseCase
from use_cases.user.user_helpers import encrypt_password, generate_password, verify_password


def test_password_round_trip():
    hashed = encrypt_password("ValidPass1!")
    assert verify_password("ValidPass1!", hashed)
    assert not verify_password("ValidPass2!", hashed)


def test_verify_password_rejects_malformed_hash():
    assert not verify_password("ValidPass1!", "not-a-hash")
    assert not verify_password("ValidPass1!", "10$zz$abcd")


def test_generated_password_meets_policy():
    password = generate_password()
    assert AuthorizationUseCase.password_invalid(password) == []


def test_password_policy_reports_each_missing_rule():
    assert AuthorizationUseCase.password_invalid("") == [
        ValidationErrorCodeEnum.PASSWORD_MISSING_LENGTH
    ]
    reasons = AuthorizationUseCase.password_invalid("short")
    assert ValidationErrorCodeEnum.PASSWORD_MISSING_LENGTH in reasons
    assert ValidationErrorCodeEnum.PASSWORD_MISSING_NUMBERS in reasons
    assert ValidationErrorCodeEnum.PASSWORD_MISSING_UPPERCASE_LOWERCASE in reasons
    assert ValidationErrorCodeEnum.PASSWORD_MISSING_SPECIAL_CHARS in reasons
