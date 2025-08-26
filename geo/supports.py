import os
import re
from tempfile import mkstemp
from typing import Dict
from zipfile import ZipFile
import xml.etree.ElementTree as ET


def prepare_zip_file(name: str, data: Dict) -> str:
    """Creates a zip file from

    GeoServer's REST API uses ZIP archives as containers for file formats such
    as Shapefile and WorldImage which include several 'boxcar' files alongside
    the main data.  In such archives, GeoServer assumes that all of the relevant
    files will have the same base name and appropriate extensions, and live in
    the root of the ZIP archive.  This method produces a zip file that matches
    these expectations, based on a basename, and a dict of extensions to paths or
    file-like objects. The client code is responsible for deleting the zip
    archive when it's done.

    Parameters
    ----------
    name : name of files
    data : dict

    Returns
    -------
    str
    """
    fd, path = mkstemp()
    zip_file = ZipFile(path, "w", allowZip64=True)
    print(fd, path, zip_file, data)
    for ext, stream in data.items():
        fname = "{}.{}".format(name, ext)
        if isinstance(stream, str):
            zip_file.write(stream, fname)
        else:
            zip_file.writestr(fname, stream.read())
    zip_file.close()
    os.close(fd)
    return path


def is_valid_xml(xml_string: str) -> bool:

    """
    Returns True if string is valid XML, false otherwise

        Parameters
    ----------
    xml_string : string containing xml

    Returns
    -------
    bool
    """

    try:
        # Attempt to parse the XML string
        ET.fromstring(xml_string)
        return True
    except ET.ParseError:
        return False


def is_surrounded_by_quotes(text, param):
    # The regex pattern searches for '%foo%' surrounded by single quotes.
    # It uses \'%foo%\' to match '%foo%' literally, including the single quotes.
    pattern = rf"\'%{param}%\'"

    # re.search() searches the string for the first location where the regex pattern produces a match.
    # If a match is found, re.search() returns a match object. Otherwise, it returns None.
    match = re.search(pattern, text)

    # Return True if a match is found, False otherwise.
    return bool(match)
