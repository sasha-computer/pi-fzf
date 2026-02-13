"""Tests for shell integration strings."""

from pi_fzf.shell import BASH_INIT, FISH_INIT, SHELLS, ZSH_INIT


def test_fish_init_contains_widget() -> None:
    assert "pi-fzf-widget" in FISH_INIT


def test_fish_init_binds_alt_p() -> None:
    assert "\\ep" in FISH_INIT


def test_bash_init_contains_widget() -> None:
    assert "pi-fzf-widget" in BASH_INIT


def test_bash_init_uses_bind() -> None:
    assert "bind -x" in BASH_INIT


def test_zsh_init_contains_widget() -> None:
    assert "pi-fzf-widget" in ZSH_INIT


def test_zsh_init_uses_bindkey() -> None:
    assert "bindkey" in ZSH_INIT


def test_shells_dict_has_all() -> None:
    assert set(SHELLS.keys()) == {"fish", "bash", "zsh"}
