import logging

import device
import probe
from register import *
import utils
import time
from copy import copy

log = logging.getLogger(__name__)


class ShellyEnergyMeter(device.EnergyMeter):
    def read_register(self, reg):
        rr = self.modbus.read_input_registers(reg.base, reg.count,
                                              unit=self.unit)

        if rr.isError():
            log.info('Error reading register %#04x: %s', reg.base, rr)
            raise Exception(rr)

        reg.decode(rr.registers)
        return reg.value

    def read_data_regs(self, regs, d):
        now = time.time()

        if all(now - r.time < r.max_age for r in regs):
            return

        start = regs[0].base
        count = regs[-1].base + regs[-1].count - start

        rr = self.modbus.read_input_registers(start, count, unit=self.unit)

        latency = time.time() - now

        if rr.isError():
            log.error('Error reading registers %#04x-%#04x: %s',
                      start, start + count - 1, rr)
            raise Exception(rr)

        for reg in regs:
            base = reg.base - start
            end = base + reg.count

            if now - reg.time > reg.max_age:
                if reg.decode(rr.registers[base:end]) or not reg.time:
                    if reg.name:
                        d[reg.name] = copy(reg) if reg.isvalid() else None
            reg.time = now

        return latency

    def get_ident(self):
        return 'shelly_{}'.format(self.info['/Serial'])
    
class ShellyEnergyMeterPro3EM(device.CustomName, ShellyEnergyMeter):
    productid = 0xB00D
    productname = 'Shelly Pro 3EM'
    nr_phases = 3

    fast_regs = (
        '/Ac/L1/Power',
        '/Ac/L2/Power',
        '/Ac/L3/Power',
        '/Ac/Power',
        '/Ac/L1/Voltage',
        '/Ac/L2/Voltage',
        '/Ac/L3/Voltage',
        '/Ac/L1/Current',
        '/Ac/L2/Current',
        '/Ac/L3/Current',
    )

    def device_init(self):
        self.info_regs = [
            Reg_text(0, 6, '/Serial', little=True)
        ]

        self.read_info();

        self.data_regs = [
            Reg_f32l(1013, '/Ac/Power', 1, '%.1f W'),
            [
                Reg_f32l(1020, '/Ac/L1/Voltage', 1, '%.1f V'),
                Reg_f32l(1022, '/Ac/L1/Current', 1, '%.1f A'),
                Reg_f32l(1024, '/Ac/L1/Power', 1, '%.1f W')
            ],
            [
                Reg_f32l(1040, '/Ac/L2/Voltage', 1, '%.1f V'),
                Reg_f32l(1042, '/Ac/L2/Current', 1, '%.1f A'),
                Reg_f32l(1044, '/Ac/L2/Power', 1, '%.1f W')
            ],
            [
                Reg_f32l(1060, '/Ac/L3/Voltage', 1, '%.1f V'),
                Reg_f32l(1062, '/Ac/L3/Current', 1, '%.1f A'),
                Reg_f32l(1064, '/Ac/L3/Power', 1, '%.1f W')
            ],
            [
                Reg_f32l(1162, '/Ac/Energy/Forward', 1000, '%.1f kWh'),
                Reg_f32l(1164, '/Ac/Energy/Reverse', 1000, '%.1f kWh')
            ],
            [
                Reg_f32l(1182, '/Ac/L1/Energy/Forward', 1000, '%.1f kWh'),
                Reg_f32l(1184, '/Ac/L1/Energy/Reverse', 1000, '%.1f kWh')
            ],
            [
                Reg_f32l(1202, '/Ac/L2/Energy/Forward', 1000, '%.1f kWh'),
                Reg_f32l(1204, '/Ac/L2/Energy/Reverse', 1000, '%.1f kWh')
            ],
            [
                Reg_f32l(1222, '/Ac/L3/Energy/Forward', 1000, '%.1f kWh'),
                Reg_f32l(1224, '/Ac/L3/Energy/Reverse', 1000, '%.1f kWh')
            ]
        ]


class ModelRegisterShelly(probe.ModelRegister):
    def probe(self, spec, modbus, timeout=None):
        with modbus, utils.timeout(modbus, timeout or self.timeout):
            if not modbus.connect():
                raise Exception('connection error')
            rr = modbus.read_input_registers(self.reg.base, self.reg.count,
                unit=spec.unit)

        if rr.isError():
            log.debug('%s: %s', modbus, rr)
            return None

        self.reg.decode(rr.registers)

        if self.reg.value in self.models:
            m = self.models[self.reg.value]
            return m['handler'](spec, modbus, m['model'])

models = {
    'SPEM-003CEBEU': {
        'model': 'SPEM-003CE',
        'handler': ShellyEnergyMeterPro3EM
    }
}

probe.add_handler(ModelRegisterShelly(Reg_text(6, 10, 'model', little=True), models,
                                      methods=['tcp'],
                                      units=[1]))
