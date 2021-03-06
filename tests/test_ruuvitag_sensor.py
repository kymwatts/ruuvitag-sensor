from unittest import TestCase
from unittest.mock import patch

from ruuvitag_sensor.ruuvi import RuuviTagSensor


class TestRuuviTagSensor(TestCase):

    def get_data(self, mac):
        # https://ruu.vi/#AjwYAMFc
        data = '043E2A0201030157168974A5F41E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'
        return data[26:]

    @patch('ruuvitag_sensor.ble_communication.BleCommunicationNix.get_data',
           get_data)
    @patch('ruuvitag_sensor.ble_communication.BleCommunicationDummy.get_data',
           get_data)
    def test_tag_update_is_valid(self):
        tag = RuuviTagSensor('48:2C:6A:1E:59:3D')

        state = tag.state
        self.assertEqual(state, {})

        state = tag.update()
        self.assertEqual(state['temperature'], 24)
        self.assertEqual(state['pressure'], 995)
        self.assertEqual(state['humidity'], 30)

    def test_false_mac_raise_error(self):
        with self.assertRaises(ValueError):
            RuuviTagSensor('48:2C:6A:1E')

    def test_tag_correct_properties(self):
        org_mac = 'AA:2C:6A:1E:59:3D'
        tag = RuuviTagSensor(org_mac)

        mac = tag.mac
        state = tag.state
        self.assertEqual(mac, org_mac)
        self.assertEqual(state, {})

    def get_datas(self):
        datas = [
            ('AA:2C:6A:1E:59:3D', '1E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'),
            ('BB:2C:6A:1E:59:3D', 'some other device'),
            ('CC:2C:6A:1E:59:3D', '1E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'),
            ('DD:2C:6A:1E:59:3D', '1E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD')
        ]

        for data in datas:
            yield data

    @patch('ruuvitag_sensor.ble_communication.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.ble_communication.BleCommunicationNix.get_datas',
           get_datas)
    def test_find_tags(self):
        tags = RuuviTagSensor.find_ruuvitags()
        self.assertEqual(3, len(tags))

    @patch('ruuvitag_sensor.ble_communication.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.ble_communication.BleCommunicationNix.get_datas',
           get_datas)
    def test_get_data_for_sensors(self):
        macs = ['CC:2C:6A:1E:59:3D', 'DD:2C:6A:1E:59:3D']
        data = RuuviTagSensor.get_data_for_sensors(macs, 4)
        self.assertEqual(2, len(data))
        self.assertTrue('CC:2C:6A:1E:59:3D' in data)
        self.assertTrue('DD:2C:6A:1E:59:3D' in data)
        self.assertTrue(data['CC:2C:6A:1E:59:3D']['temperature'] == 24.0)

    def test_convert_data_not_valid(self):
        encoded = RuuviTagSensor.convert_data('not_valid')
        self.assertIsNone(encoded)

    @patch('ruuvitag_sensor.ble_communication.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.ble_communication.BleCommunicationNix.get_datas',
           get_datas)
    def test_get_datas(self):
        datas = []
        RuuviTagSensor.get_datas(lambda x: datas.append(x))
        self.assertEqual(3, len(datas))

    @patch('ruuvitag_sensor.ble_communication.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.ble_communication.BleCommunicationNix.get_datas',
           get_datas)
    def test_get_datas_with_macs(self):
        datas = []
        macs = ['CC:2C:6A:1E:59:3D', 'DD:2C:6A:1E:59:3D']
        RuuviTagSensor.get_datas(lambda x: datas.append(x), macs)
        self.assertEqual(2, len(datas))
