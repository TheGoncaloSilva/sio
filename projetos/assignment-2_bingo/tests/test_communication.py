import pytest
import sys
from unittest.mock import Mock
from unittest.mock import MagicMock
pytest_plugins = ('pytest_asyncio',)

from common.communication import *
#from common.asymetric import *

def test_json_to_bytes():
    testDict = {"type":"msg", "player":"test", "message":"good game"}
    
    assert json_to_bytes(testDict) == b'eyJ0eXBlIjogIm1zZyIsICJwbGF5ZXIiOiAidGVzdCIsICJtZXNzYWdlIjogImdvb2QgZ2FtZSJ9'


def test_bytes_to_json():
    testBytes = b'eyJ0eXBlIjogIm1zZyIsICJwbGF5ZXIiOiAidGVzdCIsICJtZXNzYWdlIjogImdvb2QgZ2FtZSJ9'
    
    assert bytes_to_json(testBytes) == {"type":"msg", "player":"test", "message":"good game"}


@pytest.mark.asyncio
async def test_exact_recv():
    # Create a mock StreamReader and write some data to it
    mock_reader = Mock(spec=asyncio.streams.StreamReader)
    mock_reader.read.return_value = b'test data'
    
    # Test the exact_recv function
    assert await exact_recv(mock_reader, len(b'test data')) ==  b'test data'


@pytest.mark.asyncio
async def test_exact_send():
    # Create a mock StreamWriter and set its write method to return True
    mock_writer = Mock(spec=asyncio.streams.StreamWriter)
    mock_writer.write.return_value = True
    mock_writer.drain.return_value = asyncio.Future()
    mock_writer.drain.return_value.set_result(None)
    
    # Test the exact_send function
    assert await exact_send(mock_writer, b'test data') == True


@pytest.mark.asyncio
async def test_recv_dict():
    # Set up test data and parameters
    test_dict = {"type": "msg", "player": "test", "message": "good game"}
    json_bytes = json_to_bytes(test_dict)
    fake_signature: bytes = b'123'
    json_bytes = len(fake_signature).to_bytes(4,'big') + fake_signature + json_bytes
    header = len(json_bytes).to_bytes(4, 'big')
    

    # Create a mock StreamReader that returns the test data when read
    reader = MagicMock(asyncio.streams.StreamReader)
    reader.read.side_effect = [header, json_bytes]

    # Call the recv_dict function and check the returned value
    result = await recv_dict(reader,None)
    assert result == test_dict, f"Expected {test_dict}, got {result}"

    # Check that the correct number of bytes were read from the stream
    assert reader.read.call_count == 2, f"Expected 2 calls to read, got {reader.read.call_count}"


@pytest.mark.asyncio
async def test_send_dict():
    # Create a mock StreamWriter and set its write method to return True
    mock_writer = Mock(spec=asyncio.streams.StreamWriter)
    mock_writer.write.return_value = True
    mock_writer.drain.return_value = asyncio.Future()
    mock_writer.drain.return_value.set_result(None)

    # Create a test JSON dictionary
    testDict = {"type":"msg", "player":"test", "message":"good game"}

    # Test the send_dict function
    assert await send_dict(mock_writer, testDict) == True


@pytest.mark.asyncio
async def test_sendRecv_dict():
    #to-do
   pass
