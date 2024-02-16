import pytest
import sys
from unittest.mock import Mock
from unittest.mock import MagicMock
pytest_plugins = ('pytest_asyncio',)
from caller.caller import *
from common.asymmetric import generate_private_key, generate_public_key

@pytest.fixture
@pytest.mark.asyncio
async def created_caller():
    caller: Caller = Caller()
    ip: str = "127.0.0.1"
    port: int = 8000
    nick: str = "test_nick"
    # Generate key pair
    privKey: rsa.RSAPrivateKeyWithSerialization = generate_private_key(1024)
    pubKey: rsa.RSAPublicKey = generate_public_key(privKey)
    
    await caller.create_caller(ip, port, nick, 0, privKey, pubKey)

    return caller


@pytest.fixture
@pytest.mark.asyncio
async def start_server():
    # Create a dummy server using asyncio.start_server
    server = await asyncio.start_server(
        lambda r, w: None, '127.0.0.1', 8000
    )
    
    await asyncio.sleep(0.01) # Make sure that the server started before connecting
    server_host, server_port = server.sockets[0].getsockname()


@pytest.mark.asyncio
async def test_create_caller(start_server):
    await start_server

    caller: Caller = Caller()
    ip: str = "127.0.0.1"
    port: int = 8000
    nick: str = "test_nick"
    # Generate key pair
    privKey: rsa.RSAPrivateKeyWithSerialization = generate_private_key(1024)
    pubKey: rsa.RSAPublicKey = generate_public_key(privKey)
    
    reader, writer = await caller.create_caller(ip, port, nick, 0, privKey, pubKey)
    assert caller is not None
    assert caller.caller.nick == nick
    assert caller.caller.ip == ip
    assert caller.caller.port == port
    assert isinstance(reader, asyncio.StreamReader)
    assert isinstance(writer, asyncio.StreamWriter)

    # Close the connection and the server
    writer.close()
    await writer.wait_closed()
    #start_server.server.close()
    #await start_server.server.wait_closed()


@pytest.mark.asyncio
async def test_create_caller_type_error():
    caller: Caller = Caller()
    ip: str = "127.0.0.1"
    port: str = "8000"
    nick: int = 123
    privKey: rsa.RSAPrivateKeyWithSerialization = generate_private_key(1024)
    pubKey: rsa.RSAPublicKey = generate_public_key(privKey)
    
    with pytest.raises(TypeError):
        await caller.create_caller(ip, port, nick, privKey, pubKey) # type: ignore


@pytest.mark.asyncio
async def test_create_caller_value_error():
    caller: Caller = Caller()
    ip: str = "127.0.0.1"
    port: int = 8000
    nick: str = "test_nick"
    privKey: rsa.RSAPrivateKeyWithSerialization = generate_private_key(1024)
    pubKey: rsa.RSAPublicKey = generate_public_key(privKey)
    
    caller.caller = "dummy" # type: ignore
    with pytest.raises(ValueError):
        await caller.create_caller(ip, port, nick, 0, privKey, pubKey) # type: ignore


@pytest.mark.asyncio
async def test_create_caller_connection_error():
    caller: Caller = Caller()
    ip: str = "127.0.0.1"
    port: int = 12345
    nick: str = "test_nick"
    privKey: rsa.RSAPrivateKeyWithSerialization = generate_private_key(1024)
    pubKey: rsa.RSAPublicKey = generate_public_key(privKey)
    
    caller.caller = None # type: ignore
    with pytest.raises(OSError):
        await caller.create_caller(ip, port, nick, 0, privKey, pubKey)

#@pytest.mark.asyncio
#async def test_whatever(created_caller):
#    await created_caller
#    pass


