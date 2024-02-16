import pytest
import sys

from common.entity import Banned_Reason , Bans


def test_add_ban():
    ban: Bans = Bans()
    ban.add_ban(5 , Banned_Reason.BAD_SIGNATURE)
    
    with pytest.raises(ValueError):
        ban.add_ban(5 , Banned_Reason.BAD_WINNER)

    
    assert ban.is_banned(5)

    assert not ban.is_banned(6)

def test_get_ban_reason():
    ban: Bans = Bans()
    ban.add_ban(5 , Banned_Reason.BAD_SIGNATURE)

    assert ban.ban_reason(5) == Banned_Reason.BAD_SIGNATURE

    with pytest.raises(ValueError): 
        ban.ban_reason(6)

def test_get_bans():
    ban: Bans = Bans()
    ban.add_ban(5 , Banned_Reason.BAD_SIGNATURE)
    ban.add_ban(6 , Banned_Reason.BAD_WINNER)

    assert ban.get_bans() == {5 : Banned_Reason.BAD_SIGNATURE , 6 : Banned_Reason.BAD_WINNER}

def test_clear_bans():
    ban: Bans = Bans()
    ban.add_ban(5 , Banned_Reason.BAD_SIGNATURE)
    ban.clear()
    assert ban.get_bans() == {}