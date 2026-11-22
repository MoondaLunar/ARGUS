import tempfile
import unittest
from pathlib import Path
from PIL import Image
from pypdf import PdfWriter
from metadata_extractor import MetadataExtractor

class MetadataTests(unittest.TestCase):
    def test_gps_ifd_tags_and_altitude(self):
        result=MetadataExtractor.extract_gps_from_exif({34853:{1:'S',2:(12,30,0),3:'W',4:(40,0,0),5:1,6:10}})
        self.assertEqual(result.latitude,-12.5);self.assertEqual(result.longitude,-40);self.assertEqual(result.altitude,-10)

    def test_invalid_coordinates_do_not_escape(self):
        self.assertIsNone(MetadataExtractor.extract_gps_from_exif({34853:{2:(120,0,0),4:(20,0,0)}}))

    def test_missing_and_corrupt_files_return_none(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(MetadataExtractor.extract_file_metadata(str(Path(d)/'missing.pdf')))
            p=Path(d)/'broken.jpg';p.write_bytes(b'not an image')
            self.assertIsNone(MetadataExtractor.extract_file_metadata(str(p)))

    def test_blank_pdf_returns_metadata_without_text_exception(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'blank.pdf';writer=PdfWriter();writer.add_blank_page(width=100,height=100)
            with path.open('wb') as f:writer.write(f)
            result=MetadataExtractor.extract_file_metadata(str(path))
            self.assertEqual(result['pages'],1);self.assertEqual(result['text_preview'],'')

    def test_image_dimensions_without_exif(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fixture.png';Image.new('RGB',(4,6)).save(p)
            result=MetadataExtractor.extract_file_metadata(str(p))
            self.assertEqual((result['width'],result['height']),(4,6));self.assertIsNone(result['gps'])
