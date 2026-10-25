"""Verifica recursos del proyecto con el valor predeterminado cp1252 de Windows."""
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
original_read_text = Path.read_text

def windows_read_text(self, encoding=None, errors=None, **kwargs):
    if self.resolve().is_relative_to(ROOT) and encoding is None:
        raise AssertionError(f'Falta encoding explícito: {self}')
    return original_read_text(self, encoding=encoding, errors=errors, **kwargs)

with patch.object(Path, 'read_text', windows_read_text):
    from analytics import load_data
    from charts import make_chart
    from map_widget import map_html
    from notebook_ui import panel
    payload, data = load_data()
    figure, _ = make_chart('map', data, payload)
    document = map_html(figure, payload['hubs'])
    assert 'FlightMap.mount' in document
    assert 'L.map' in document
    assert len(figure.data[0].lat) == 35
    assert 'notebook-dashboard' in panel('Prueba de codificación')
    print('PASS: mapa generado, 35 aeropuertos y recursos con UTF-8 explícito.')
