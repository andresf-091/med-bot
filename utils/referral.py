def validate_referral_code(referral_code: str):
    if len(referral_code) != 20:
        return False
    if not referral_code.startswith("ref"):
        return False
    if not referral_code[3:].isalnum():
        return False
    return True


def get_sender_id(referral_code: str):
    return int(referral_code[3:])
