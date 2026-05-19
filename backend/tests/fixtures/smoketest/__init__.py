"""Smoke-test fixtures for the dispatcher's end-to-end verification.

These entities + commands exist only to exercise the M0.3 dispatcher
pipeline without depending on any real domain code. They live under
tests/fixtures/ rather than app/ per Session 30 Q2 -- clean production
surface; the fake entities never ship.
"""
