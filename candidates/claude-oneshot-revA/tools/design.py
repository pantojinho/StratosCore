"""StratosCore Rev A - Claude one-shot candidate: complete netlist-first circuit description.

Every part states (reference, library symbol, value, footprint, pin -> net). Values that are
not closed by a cited source carry "TBD" in the value or in the `Status` field. Sources are
the repository documents (docs/*.md) and the manufacturer data sheets named in `Source`.

Status of this file: CANDIDATE for comparison with the Astra pass. It does NOT satisfy the
docs/ASTRA_HANDOFF.md entry gates and is not a manufacturing release.
"""
from __future__ import annotations

from dataclasses import dataclass, field

PLIB = "SC"            # project symbol + footprint library nickname

FP = {
    "R0402": "Resistor_SMD:R_0402_1005Metric",
    "R0603": "Resistor_SMD:R_0603_1608Metric",
    "R1206": "Resistor_SMD:R_1206_3216Metric",
    "R2512": "Resistor_SMD:R_2512_6332Metric",
    "C0402": "Capacitor_SMD:C_0402_1005Metric",
    "C0603": "Capacitor_SMD:C_0603_1608Metric",
    "C0805": "Capacitor_SMD:C_0805_2012Metric",
    "C1206": "Capacitor_SMD:C_1206_3216Metric",
    "TP": "TestPoint:TestPoint_Pad_D1.0mm",
}

# rails drawn with power symbols (net name == symbol value)
RAILS = ["GND", "VBUS", "VBUS_PROT", "PACK_P", "BAT_P", "BAT_MID", "BAT_N", "3V3_MAIN",
         "3V3_GNSS", "3V3_SD", "3V3_ADSB", "3V0_RF_QUIET", "1V8_LOGIC", "1V8_AUDIO_SW",
         "1V1_ADSB", "3V3_EXP", "CHG_REGN"]


@dataclass
class Part:
    ref: str
    lib_id: str
    value: str
    footprint: str
    conns: dict
    fields: dict = field(default_factory=dict)
    dnp: bool = False
    group: str = ""


@dataclass
class SheetDef:
    name: str
    file: str
    title: str
    notes: list
    parts: list = field(default_factory=list)
    flags: list = field(default_factory=list)


class Design:
    def __init__(self):
        self.sheets: list = []
        self.cur: SheetDef | None = None
        self.group = ""
        self.refs: set = set()

    def sheet(self, name, file, title, notes):
        self.cur = SheetDef(name, file, title, notes)
        self.sheets.append(self.cur)
        self.group = ""

    def g(self, name):
        self.group = name

    def add(self, ref, lib_id, value, footprint, conns, mpn="", status="", source="", dnp=False, **extra):
        if ref in self.refs:
            raise ValueError(f"duplicate ref {ref}")
        self.refs.add(ref)
        f = {}
        if mpn:
            f["MPN"] = mpn
        if status:
            f["Status"] = status
        if source:
            f["Source"] = source
        f.update(extra)
        self.cur.parts.append(Part(ref, lib_id, value, footprint, dict(conns), f, dnp, self.group))

    def R(self, ref, value, a, b, fp="R0402", dnp=False, status="", **kw):
        self.add(ref, "Device:R_Small", value, FP[fp], {"1": a, "2": b}, dnp=dnp, status=status, **kw)

    def C(self, ref, value, a, b="GND", fp="C0402", dnp=False, status="", **kw):
        self.add(ref, "Device:C_Small", value, FP[fp], {"1": a, "2": b}, dnp=dnp, status=status, **kw)

    def TP(self, ref, net):
        self.add(ref, "Connector:TestPoint", "TP", FP["TP"], {"1": net})

    def flag(self, net):
        self.cur.flags.append(net)


# --------------------------------------------------------------------------- custom symbols
# (number, name, electrical type, side). Pin tables transcribed from the cited data sheets.
S = "power_in"
CUSTOM = {
    "TPS259474L": dict(ref="U", fp=f"{PLIB}:TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm",
        ds="https://www.ti.com/lit/ds/symlink/tps25947.pdf (SLVSFC9C, pin table + RPW0010A drawing 4225183/A)",
        pins=[("5", "IN", S, "L"), ("1", "EN/UVLO", "input", "L"), ("2", "OVLO", "input", "L"),
              ("4", "PGTH", "input", "L"), ("6", "OUT", "power_out", "R"), ("3", "PG", "open_collector", "R"),
              ("9", "ILM", "passive", "R"), ("10", "ITIMER", "passive", "R"), ("7", "DVDT", "passive", "R"),
              ("8", "GND", S, "B")]),
    "SN74AXC4T245PW": dict(ref="U", fp="Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
        ds="https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf (SCES877B pin table)",
        pins=[("1", "VCCA", S, "T"), ("16", "VCCB", S, "T"), ("2", "1DIR", "input", "L"), ("3", "2DIR", "input", "L"),
              ("15", "~{1OE}", "input", "L"), ("14", "~{2OE}", "input", "L"), ("4", "1A1", "bidirectional", "L"),
              ("5", "1A2", "bidirectional", "L"), ("6", "2A1", "bidirectional", "L"), ("7", "2A2", "bidirectional", "L"),
              ("13", "1B1", "bidirectional", "R"), ("12", "1B2", "bidirectional", "R"), ("11", "2B1", "bidirectional", "R"),
              ("10", "2B2", "bidirectional", "R"), ("8", "GND", S, "B"), ("9", "GND", "passive", "B")]),
    "TPS61169": dict(ref="U", fp=f"{PLIB}:TI_DCK0005A_SC-70-5_TPS61169",
        ds="https://www.ti.com/lit/ds/symlink/tps61169.pdf (SNVSA40B Table 4-1)",
        pins=[("5", "VIN", S, "L"), ("4", "CTRL", "input", "L"), ("1", "SW", "passive", "R"),
              ("3", "FB", "input", "R"), ("2", "GND", S, "B")]),
    "TXU0202DCU": dict(ref="U", fp="Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        ds="https://www.ti.com/lit/ds/symlink/txu0202.pdf (SCES942A pin table; A1->B1Y, B2->A2Y)",
        pins=[("3", "VCCA", S, "T"), ("7", "VCCB", S, "T"), ("5", "A1", "input", "L"), ("4", "A2Y", "output", "L"),
              ("6", "OE", "input", "L"), ("8", "B1Y", "output", "R"), ("1", "B2", "input", "R"), ("2", "GND", S, "B")]),
    "TPS22918": dict(ref="U", fp=f"{PLIB}:TI_DBV0006A_SOT-23-6_TPS22918",
        ds="https://www.ti.com/lit/ds/symlink/tps22918.pdf (SLVSD76C pin table)",
        pins=[("1", "VIN", S, "L"), ("3", "ON", "input", "L"), ("4", "CT", "passive", "L"),
              ("6", "VOUT", "power_out", "R"), ("5", "QOD", "passive", "R"), ("2", "GND", S, "B")]),
    "TPD1E0B04": dict(ref="D", fp=f"{PLIB}:TI_TPD1E0B04DPYR_X1SON-2_DPY0002A",
        ds="https://www.ti.com/lit/ds/symlink/tpd1e0b04.pdf (SLVSDG9C: two symmetric IO pins)",
        pins=[("1", "IO", "passive", "L"), ("2", "IO", "passive", "R")]),
    "DUAL_NMOS_S1G1D2S2G2D1": dict(ref="Q", fp="Package_TO_SOT_SMD:SOT-23-6",
        ds="Generic dual N-MOSFET pin order S1 G1 D2 S2 G2 D1 (exact MPN TBD, O05)",
        pins=[("1", "S1", "passive", "L"), ("2", "G1", "input", "L"), ("6", "D1", "passive", "L"),
              ("4", "S2", "passive", "R"), ("5", "G2", "input", "R"), ("3", "D2", "passive", "R")]),
    "ICM-42688-P": dict(ref="U", fp=f"{PLIB}:TDK_ICM-42688-P_LGA-14_3x2.5mm_P0.5mm",
        ds="TDK DS-000347 v1.9 pin table (pin 7 RESV must be GND; 2/3/10/11 NC or GND)",
        pins=[("8", "VDD", S, "T"), ("5", "VDDIO", S, "T"), ("14", "AP_SDA", "bidirectional", "L"),
              ("13", "AP_SCL", "input", "L"), ("12", "AP_CS", "input", "L"), ("1", "AP_SDO/AD0", "bidirectional", "L"),
              ("4", "INT1", "output", "R"), ("9", "INT2/FSYNC", "bidirectional", "R"), ("2", "RESV", "passive", "R"),
              ("3", "RESV", "passive", "R"), ("10", "RESV", "passive", "R"), ("11", "RESV", "passive", "R"),
              ("7", "RESV_GND", "passive", "B"), ("6", "GND", S, "B")]),
    "BMP581": dict(ref="U", fp=f"{PLIB}:Bosch_BMP581_LGA-10_2x2mm_CORRECTED",
        ds="Bosch BST-BMP581-DS004-13 pin table",
        pins=[("10", "VDD", S, "T"), ("1", "VDDIO", S, "T"), ("4", "SDI", "bidirectional", "L"), ("2", "SCK", "input", "L"),
              ("6", "CSB", "input", "L"), ("5", "SDO", "bidirectional", "L"), ("7", "INT", "output", "R"),
              ("3", "VSS", S, "B"), ("8", "VSS", "passive", "B"), ("9", "VSS", "passive", "B")]),
    "MMC5983MA": dict(ref="U", fp=f"{PLIB}:MEMSIC_MMC5983MA_LGA-16_3x3mm_P0.5mm_CORRECTED",
        ds="MEMSIC MMC5983MA Rev A pin table (CAP 10uF)",
        pins=[("2", "VDD", S, "T"), ("13", "VDDIO", S, "T"), ("16", "SDA/SDI", "bidirectional", "L"),
              ("1", "SCL/SCK", "input", "L"), ("4", "SPI_CS", "input", "L"), ("5", "SPI_SDO", "output", "L"),
              ("15", "INT", "output", "R"), ("10", "CAP", "passive", "R"), ("3", "NC", "passive", "R"),
              ("6", "NC", "passive", "R"), ("7", "NC", "passive", "R"), ("8", "NC", "passive", "R"),
              ("12", "NC", "passive", "R"), ("14", "NC", "passive", "R"), ("9", "GND", S, "B"), ("11", "GND", "passive", "B")]),
    "T5838": dict(ref="MK", fp=f"{PLIB}:TDK_T5838_LGA-7_3.5x2.65mm_BottomPort",
        ds="TDK DS-000383 (rev 1.0 retrieved; rev 1.1 cited in repo) Table 10",
        pins=[("7", "VDD", S, "T"), ("6", "CLK", "input", "L"), ("2", "SELECT", "input", "L"), ("5", "THSEL", "input", "L"),
              ("1", "DATA", "output", "R"), ("4", "WAKE", "output", "R"), ("3", "GND", S, "B")]),
    "S-8252": dict(ref="U", fp="Package_TO_SOT_SMD:SOT-23-6",
        ds="ABLIC S-8252 Rev 4.0 SOT-23-6 pin table; product code TBD (O05)",
        pins=[("5", "VDD", S, "L"), ("4", "VC", S, "L"), ("6", "VSS", S, "L"), ("1", "DO", "output", "R"),
              ("2", "CO", "output", "R"), ("3", "VM", "input", "R")]),
    "BLB01": dict(ref="U", fp=f"{PLIB}:BeRex_BLB01_DFN-8-1EP_2x2mm_P0.5mm",
        ds="BeRex BLB01 rev 6.6 pin table",
        pins=[("2", "RFIN", "passive", "L"), ("1", "VEN/VBIAS", "passive", "L"), ("7", "RFOUT/VDD", "passive", "R"),
              ("3", "NC", "passive", "R"), ("4", "NC", "passive", "R"), ("5", "NC", "passive", "R"), ("6", "NC", "passive", "R"),
              ("8", "NC", "passive", "R"), ("9", "GND", S, "B")]),
    "TA2003A": dict(ref="FL", fp=f"{PLIB}:TAI-SAW_TA2003A_SMD-6_3.0x3.0mm",
        ds="TAI-SAW TA2003A spec rev 1 (B input, E output, A/C/D/F GND)",
        pins=[("B", "IN", "passive", "L"), ("E", "OUT", "passive", "R"), ("A", "GND", "passive", "B"),
              ("C", "GND", "passive", "B"), ("D", "GND", "passive", "B"), ("F", "GND", "passive", "B")]),
    "ADL5513": dict(ref="U", fp="Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm",
        ds="ADI ADL5513 Rev B pin table (CP-16-22); EP size TBD from ADI drawing",
        pins=[("1", "VPOS", S, "T"), ("4", "VPOS", "passive", "T"), ("2", "INHI", "input", "L"), ("3", "INLO", "input", "L"),
              ("9", "TADJ", "input", "L"), ("14", "CLPF", "passive", "L"), ("12", "VOUT", "output", "R"),
              ("11", "VSET", "input", "R"), ("5", "NC", "passive", "R"), ("6", "NC", "passive", "R"), ("7", "NC", "passive", "R"),
              ("8", "NC", "passive", "R"), ("13", "NC", "passive", "R"), ("15", "NC", "passive", "R"), ("16", "NC", "passive", "R"),
              ("10", "COMM", S, "B"), ("17", "EPAD", "passive", "B")]),
    "PE4259": dict(ref="U", fp="Package_TO_SOT_SMD:SOT-363_SC-70-6",
        ds="pSemi PE4259 DOC-03694 pin table",
        pins=[("5", "RFC", "passive", "L"), ("4", "CTRL", "input", "L"), ("6", "VDD/CTRL_N", "input", "L"),
              ("1", "RF1", "passive", "R"), ("3", "RF2", "passive", "R"), ("2", "GND", S, "B")]),
    "BAT_HOLDER_2S_21700": dict(ref="BT", fp=f"{PLIB}:BatteryHolder_2S_21700_TBD",
        ds="docs/POWER_ARCHITECTURE_REVIEW.md - holder MPN TBD; needs B-/MID/B+ terminals",
        pins=[("1", "B+", "passive", "R"), ("2", "MID", "passive", "R"), ("3", "B-", "passive", "R")]),
}


def build() -> Design:
    d = Design()
    ESP_REF = "U1"

    # ======================================================================= 01 USB input
    d.sheet("01 USB-C input", "01_usb_input.kicad_sch", "01 USB-C input, VBUS eFuse, CC controller, USB ESD", [
        "Fixed UFP sink, no USB PD, 5 V only (D12/P17). TUSB320LAI in GPIO mode (D22): PORT=GND, ADDR=NC, EN_N=GND, OUT1-3 read by TCA9535.",
        "TPS259474L values from docs/POWER_INPUT_EVIDENCE.md (PWR-02): RILM 1.69k, UVLO 232k/100k, OVLO 442k/100k, dVdt open. ITIMER TBD (O06): C9 DNP.",
        "PGTH divider (R8/R9) is a candidate choice of this one-shot (same ratio as UVLO); review with O06. Shield treatment TBD: R1 0R placeholder.",
    ])
    d.g("usbc")
    d.add("J1", "Connector:USB_C_Receptacle_USB2.0_16P", "USB4105-GF-A",
          "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
          {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": "VBUS", "A9": "VBUS", "B4": "VBUS",
           "B9": "VBUS", "A5": "USB_CC1", "B5": "USB_CC2", "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DN",
           "B7": "USB_DN", "A8": "", "B8": "", "SH": "USB_SHIELD"},
          mpn="USB4105-GF-A", status="PREFERRED CANDIDATE - drawing B4 second pass open",
          source="https://gct.co/files/drawings/usb4105.pdf")
    d.R("R1", "0R", "USB_SHIELD", "GND", status="Shield/chassis treatment TBD")
    d.add("U2", "Power_Protection:TPD4E05U06DQA", "TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
          {"1": "USB_DP", "2": "USB_DN", "4": "USB_CC1", "5": "USB_CC2", "3": "GND", "8": "GND",
           "6": "", "7": "", "9": "", "10": ""}, mpn="TPD4E05U06DQARG4", source="TI SLVSBO7O")
    d.C("C1", "1uF 25V X7R", "VBUS", fp="C0603")
    d.g("efuse")
    d.add("U3", f"{PLIB}:TPS259474L", "TPS259474LRPWR", CUSTOM["TPS259474L"]["fp"],
          {"5": "VBUS", "6": "VBUS_PROT", "1": "EFUSE_UV", "2": "EFUSE_OV", "3": "EFUSE_PG", "4": "EFUSE_PGTH",
           "9": "EFUSE_ILM", "10": "EFUSE_ITIMER", "7": "", "8": "GND"},
          mpn="TPS259474LRPWR", status="CANDIDATE - O05/O06 review", source="TI SLVSFC9C")
    d.R("R2", "232k 1%", "VBUS", "EFUSE_UV")
    d.R("R3", "100k 1%", "EFUSE_UV", "GND")
    d.R("R4", "442k 1%", "VBUS", "EFUSE_OV")
    d.R("R5", "100k 1%", "EFUSE_OV", "GND")
    d.R("R6", "1.69k 1%", "EFUSE_ILM", "GND")
    d.R("R7", "100k", "EFUSE_PG", "3V3_MAIN")
    d.R("R8", "232k 1%", "VBUS_PROT", "EFUSE_PGTH", status="one-shot candidate")
    d.R("R9", "100k 1%", "EFUSE_PGTH", "GND", status="one-shot candidate")
    d.C("C9", "TBD (O06)", "EFUSE_ITIMER", dnp=True, status="ITIMER value TBD at O06")
    d.C("C2", "1uF 25V X7R", "VBUS_PROT", fp="C0603")
    d.TP("TP1", "VBUS")
    d.TP("TP2", "EFUSE_PG")
    d.g("tusb")
    d.add("U4", "Interface_USB:TUSB320I", "TUSB320LAIRWBR", f"{PLIB}:TI_RWB0012B_X2QFN-12_1.6x1.6mm_TUSB320LAI",
          {"1": "USB_CC1", "2": "USB_CC2", "3": "GND", "4": "TUSB_VDET", "5": "", "6": "TUSB_OUT3",
           "7": "TUSB_OUT1", "8": "TUSB_OUT2", "9": "", "10": "GND", "11": "GND", "12": "3V3_MAIN"},
          mpn="TUSB320LAIRWBR", source="TI SLLSEQ8D (pin map identical to KiCad TUSB320 symbol)")
    d.R("R10", "900k 1%", "VBUS", "TUSB_VDET", status="data-sheet 900k")
    d.C("C3", "100nF", "3V3_MAIN")
    d.R("R11", "100k", "TUSB_OUT1", "3V3_MAIN")
    d.R("R12", "100k", "TUSB_OUT2", "3V3_MAIN")
    d.R("R13", "100k", "TUSB_OUT3", "3V3_MAIN")
    d.flag("VBUS")
    d.flag("GND")

    # ======================================================================= 02 battery + charger
    d.sheet("02 2S battery, protection, charger", "02_battery_charger.kicad_sch",
            "02 2S 21700 holder, common protection (O05 HOLD), BQ25887 balanced charger", [
        "*** O05: battery protection/charger topology REQUIRES QUALIFIED HUMAN REVIEW. This sheet is a candidate only; do not energize. ***",
        "Low-side common protection (S-8252 family + dual N-FET, product code/FETs/fuse TBD) is shown in the documented conflicting position: charger GND = pack negative after cutoff.",
        "BQ25887 per SLUSD89B Fig.69: 1uH PMID-SW, 47nF BTST, 4.7uF REGN, 10uF PMID, 44uF SNS, 10uF BAT, TS 5.23k/30.1k + 10k NTC, 300R MID limiter.",
        "Fail-safe CD: pulled to REGN (charging disabled whenever VBUS is present) until firmware drives CHG_EN (TCA9535 P17) -> Q2 pulls CD low. RILIM 2.21k -> 502 mA (KILIM 1110). PSEL high.",
        "Dead-pack deadlock (MCU cannot enable charging if pack is empty) is an open O05 item; R26 (DNP) is a service override only.",
    ])
    d.g("cells")
    d.add("BT1", f"{PLIB}:BAT_HOLDER_2S_21700", "2S 21700 holder (MPN TBD)", CUSTOM["BAT_HOLDER_2S_21700"]["fp"],
          {"1": "BAT_P", "2": "BAT_MID", "3": "BAT_N"}, mpn="TBD", status="OWNER DIRECTION - MPN/REVIEW TBD")
    d.add("F1", "Device:Fuse", "TBD (O05)", "Fuse:Fuse_1206_3216Metric", {"1": "BAT_P", "2": "PACK_P"},
          status="Rating/type TBD by qualified review (O05)")
    d.flag("BAT_P")
    d.flag("BAT_MID")
    d.flag("BAT_N")
    d.flag("PROT_VDD")
    d.flag("PROT_VC")
    d.TP("TP3", "PACK_P")
    d.TP("TP4", "BAT_MID")
    d.g("prot")
    d.add("U5", f"{PLIB}:S-8252", "S-8252 (product code TBD, O05)", CUSTOM["S-8252"]["fp"],
          {"5": "PROT_VDD", "4": "PROT_VC", "6": "BAT_N", "1": "PROT_DO", "2": "PROT_CO", "3": "PROT_VM"},
          status="CANDIDATE FAMILY - TOPOLOGY CONFLICT - QUALIFIED REVIEW (O05)", source="ABLIC S-8252 Rev 4.0 Fig.14/Table 11")
    d.R("R60", "470R", "BAT_P", "PROT_VDD", status="ABLIC Table 11 typ")
    d.C("C62", "100nF", "PROT_VDD", "BAT_N")
    d.R("R61", "470R", "BAT_MID", "PROT_VC", status="ABLIC Table 11 typ; R1*C1 = R2*C2")
    d.C("C63", "100nF", "PROT_VC", "BAT_N")
    d.R("R62", "2k", "PROT_VM", "GND", status="ABLIC Table 11 typ")
    d.add("Q1", f"{PLIB}:DUAL_NMOS_S1G1D2S2G2D1", "Dual N-MOSFET TBD (O05)", "Package_TO_SOT_SMD:SOT-23-6",
          {"1": "BAT_N", "2": "PROT_DO", "3": "PROT_DRAIN", "4": "GND", "5": "PROT_CO", "6": "PROT_DRAIN"},
          status="PLACEHOLDER - FET selection/SOA/package TBD (O05)")
    d.g("charger")
    d.add("U6", "Battery_Management:BQ25887RGE", "BQ25887RGER",
          "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
          {"23": "VBUS_PROT", "21": "CHG_PMID", "22": "CHG_PMID", "17": "CHG_SW", "18": "CHG_SW",
           "12": "CHG_BTST", "15": "CHG_SNS", "16": "CHG_SNS", "13": "PACK_P", "14": "PACK_P",
           "9": "CHG_MID", "10": "CHG_CBSET", "11": "CHG_REGN", "7": "CHG_TS", "8": "CHG_ILIM",
           "1": "CHG_PG", "2": "CHG_STAT", "3": "CHG_CD", "4": "I2C_SDA", "5": "I2C_SCL", "6": "CHG_INT",
           "24": "CHG_PSEL", "19": "GND", "20": "GND", "25": "GND"},
          mpn="BQ25887RGER", status="PREFERRED CANDIDATE - SAFETY REVIEW (O05)", source="TI SLUSD89B")
    d.add("L1", "Device:L", "1uH (DFE252012F-1R0 class)", "Inductor_SMD:L_1008_2520Metric",
          {"1": "CHG_PMID", "2": "CHG_SW"}, status="TI Fig.69 value; saturation/DCR review")
    d.C("C10", "1uF 25V", "VBUS_PROT", fp="C0603")
    d.C("C11", "10uF 25V", "CHG_PMID", fp="C0805")
    d.C("C12", "47nF", "CHG_BTST", "CHG_SW")
    d.C("C13", "4.7uF 10V", "CHG_REGN", fp="C0603")
    d.C("C14", "22uF 16V", "CHG_SNS", fp="C0805")
    d.C("C15", "22uF 16V", "CHG_SNS", fp="C0805")
    d.C("C16", "10uF 16V", "PACK_P", fp="C0805")
    d.R("R14", "300R", "CHG_MID", "BAT_MID", fp="R0603", status="TI reverse-bottom-cell limiter")
    d.R("R15", "TBD (RCBSET)", "CHG_CBSET", "BAT_MID", fp="R2512", status="balance current TBD; 40.8R/0.41W at 100 mA planning point")
    d.R("R16", "5.23k 1%", "CHG_REGN", "CHG_TS")
    d.R("R17", "30.1k 1%", "CHG_TS", "GND")
    d.add("TH1", "Device:Thermistor_NTC", "10k NTC (103AT class, TBD)", "Resistor_SMD:R_0603_1608Metric",
          {"1": "CHG_TS", "2": "GND"}, status="thermal coupling to cells TBD")
    d.R("R18", "2.21k 1%", "CHG_ILIM", "GND", status="IINMAX = 1110/2210 = 502 mA (default-current floor)")
    d.R("R19", "10k", "CHG_PSEL", "CHG_REGN", status="PSEL high = low input-current class")
    d.R("R20", "100k", "CHG_CD", "CHG_REGN", status="fail-safe: charge disabled")
    d.add("Q2", "Transistor_FET:2N7002", "2N7002", "Package_TO_SOT_SMD:SOT-23",
          {"1": "CHG_EN", "2": "GND", "3": "CHG_CD"})
    d.R("R21", "100k", "CHG_EN", "GND")
    d.R("R26", "0R", "CHG_CD", "GND", dnp=True, status="SERVICE OVERRIDE ONLY - DNP")
    d.R("R22", "10k", "CHG_INT", "3V3_MAIN")
    d.R("R23", "10k", "CHG_STAT", "3V3_MAIN")
    d.R("R24", "10k", "CHG_PG", "3V3_MAIN")
    d.TP("TP5", "CHG_STAT")
    d.TP("TP6", "CHG_PG")

    # ======================================================================= 03 regulators
    d.sheet("03 Rails", "03_rails.kicad_sch", "03 TPS62130A 3V3_MAIN buck, TPS7A20 LDOs, branch links", [
        "TPS62130A per SLVSAG7F 9.2: 2.2uH XFL4020-222MEB, FSW=GND (2.5 MHz), DEF=GND, 312k/100k -> 3.296 V (docs/POWER_RAIL_PLAN.md).",
        "SS/TR: repo text lists 0.1uF (50 ms by Eq.10) - this candidate uses 3.3nF (about 1.65 ms, TI typical); feed-forward C24 3.3nF fitted per repo text. Reviewer to confirm.",
        "No main power switch/button is specified in the product baseline: buck EN is pulled to PACK_P (always on while the protected pack is present). Product decision gap.",
        "3V0_RF_QUIET LDO EN follows the switched 3V3_ADSB domain so the ADS-B analog chain powers down with RP2040 (one-shot proposal).",
    ])
    d.g("buck")
    d.add("U7", "Regulator_Switching:TPS62130A", "TPS62130ARGTR", f"{PLIB}:TI_RGT0016A_VQFN-16_3x3mm_EP1.75x1.75_TPS62130A",
          {"10": "PACK_P", "11": "PACK_P", "12": "PACK_P", "13": "BUCK_EN", "1": "BUCK_SW", "2": "BUCK_SW",
           "3": "BUCK_SW", "14": "3V3_MAIN", "5": "BUCK_FB", "4": "BUCK_PG", "7": "GND", "8": "GND",
           "9": "BUCK_SS", "6": "GND", "15": "GND", "16": "GND", "17": "GND"},
          mpn="TPS62130ARGTR", source="TI SLVSAG7F")
    d.add("L2", "Device:L", "2.2uH XFL4020-222MEB", f"{PLIB}:L_Coilcraft_XxL4020",
          {"1": "BUCK_SW", "2": "3V3_MAIN"}, mpn="XFL4020-222MEB")
    d.R("R27", "100k", "PACK_P", "BUCK_EN")
    d.C("C20", "10uF 25V X7R", "PACK_P", fp="C0805")
    d.C("C21", "100nF 25V", "PACK_P")
    d.C("C22", "22uF 6.3V X7R", "3V3_MAIN", fp="C0805")
    d.C("C23", "22uF 6.3V X7R", "3V3_MAIN", fp="C0805", status="second output cap; DC-bias review")
    d.R("R28", "312k 1%", "3V3_MAIN", "BUCK_FB")
    d.R("R29", "100k 1%", "BUCK_FB", "GND")
    d.C("C24", "3.3nF", "3V3_MAIN", "BUCK_FB", status="feed-forward per repo text; review")
    d.C("C25", "3.3nF", "BUCK_SS")
    d.R("R30", "100k", "BUCK_PG", "3V3_MAIN")
    d.TP("TP7", "3V3_MAIN")
    d.flag("3V3_MAIN")
    d.TP("TP8", "BUCK_SW")
    d.g("ldo30")
    d.add("U8", "Regulator_Linear:TPS7A20xxxDBV", "TPS7A2030PDBVR", f"{PLIB}:TI_DBV0005A_SOT-23-5_TPS7A20",
          {"1": "3V3_MAIN", "3": "3V3_ADSB", "5": "3V0_RF_QUIET", "2": "GND", "4": ""}, mpn="TPS7A2030PDBVR",
          source="TI SBVS338H")
    d.C("C26", "1uF", "3V3_MAIN")
    d.C("C27", "1uF", "3V0_RF_QUIET")
    d.TP("TP9", "3V0_RF_QUIET")
    d.g("ldo18")
    d.add("U9", "Regulator_Linear:TPS7A20xxxDBV", "TPS7A2018PDBVR", f"{PLIB}:TI_DBV0005A_SOT-23-5_TPS7A20",
          {"1": "3V3_MAIN", "3": "3V3_MAIN", "5": "1V8_LOGIC", "2": "GND", "4": ""}, mpn="TPS7A2018PDBVR",
          source="TI SBVS338H")
    d.C("C28", "1uF", "3V3_MAIN")
    d.C("C29", "1uF", "1V8_LOGIC")
    d.TP("TP10", "1V8_LOGIC")
    d.g("links")
    d.R("R31", "0R", "3V3_MAIN", "3V3_GNSS", fp="R0603", status="GNSS branch; bead DCR<=0.15R fallback (GNSS-01)")
    d.R("R32", "0R", "3V3_MAIN", "3V3_EXP", fp="R0603", status="expansion current limit TBD")

    # ======================================================================= 04 compute + control
    d.sheet("04 Compute and control", "04_compute.kicad_sch",
            "04 ESP32-S3-WROOM-1-N16R8, buttons, TCA9535 slow control, I2C pull-ups, expansion", [
        "GPIO allocation = docs/INTERFACE_GPIO_MAP.md. GPIO3/45/46 straps and GPIO35-37 (octal PSRAM) are no-connect.",
        "TCA9535 map = docs/CONTROL_IO_REVIEW.md DIG-03 plus ONE-SHOT PROPOSALS for the spare ports: P07 EXP_CS_N (expansion CS has no ESP32 GPIO in the map),",
        "P10 SX_NRESET (was reserved SX aux), P14 RP_RUN (DIG-01 host reset), P15 BUCK_PG (input), P17 CHG_EN (charger enable, hardware default = disabled).",
        "I2C 100 kHz, 2.2k pull-ups on 3V3_MAIN (D22). JST GH BM12B-GHS-TBT is a VERTICAL (top-entry) header in JST/KiCad naming, not right-angle as the BOM text says.",
    ])
    d.g("esp")
    d.add(ESP_REF, "RF_Module:ESP32-S3-WROOM-1", "ESP32-S3-WROOM-1-N16R8", "RF_Module:ESP32-S3-WROOM-1",
          {"1": "GND", "40": "GND", "41": "GND", "2": "3V3_MAIN", "3": "ESP_EN",
           "4": "TOUCH_INT", "5": "SX_DIO1", "6": "SX_BUSY", "7": "LCD_BL_PWM", "12": "LCD_AUX",
           "17": "SX_NSS", "18": "LCD_CS", "19": "SPI_MOSI", "20": "SPI_SCLK", "21": "SPI_MISO", "22": "SD_CS",
           "8": "PDM_CLK", "9": "PDM_DATA", "10": "GNSS_TX", "11": "GNSS_RX", "13": "USB_DN", "14": "USB_DP",
           "23": "GNSS_PPS", "31": "EXP_IRQ", "32": "EXP_UART_TX", "33": "EXP_UART_RX", "34": "RP_UART_RTS",
           "35": "RP_UART_CTS", "37": "RP_UART_TX", "36": "RP_UART_RX", "24": "IMU_INT1", "25": "BUTTON_2",
           "27": "BUTTON_1", "39": "I2C_SDA", "38": "I2C_SCL",
           "15": "", "16": "", "26": "", "28": "", "29": "", "30": ""},
          mpn="ESP32-S3-WROOM-1-N16R8", status="LOCKED", source="Espressif ESP32-S3-WROOM-1 datasheet")
    d.R("R40", "10k", "ESP_EN", "3V3_MAIN")
    d.C("C40", "1uF", "ESP_EN")
    d.C("C41", "10uF", "3V3_MAIN", fp="C0603")
    d.C("C42", "100nF", "3V3_MAIN")
    d.TP("TP11", "ESP_EN")
    d.g("buttons")
    d.add("SW1", "Switch:SW_Push", "SKSCLCE010 (BUTTON_1 / BOOT)", f"{PLIB}:SW_Alps_SKSCLCE010_SidePush",
          {"1": "BUTTON_1", "2": "GND"}, mpn="SKSCLCE010", status="footprint from SKSC drawing - review")
    d.add("SW2", "Switch:SW_Push", "SKSCLCE010 (BUTTON_2)", f"{PLIB}:SW_Alps_SKSCLCE010_SidePush",
          {"1": "BUTTON_2", "2": "GND"}, mpn="SKSCLCE010", status="footprint from SKSC drawing - review")
    d.R("R41", "10k", "BUTTON_1", "3V3_MAIN")
    d.R("R42", "10k", "BUTTON_2", "3V3_MAIN")
    d.g("i2c")
    d.R("R43", "2.2k 1%", "I2C_SDA", "3V3_MAIN")
    d.R("R44", "2.2k 1%", "I2C_SCL", "3V3_MAIN")
    d.TP("TP12", "I2C_SDA")
    d.TP("TP13", "I2C_SCL")
    d.g("tca")
    d.add("U13", "Interface_Expansion:TCA9535PWR", "TCA9535PWR", f"{PLIB}:TI_PW0024A_TSSOP-24_4.4x7.8mm_TCA9535",
          {"24": "3V3_MAIN", "12": "GND", "21": "GND", "2": "GND", "3": "GND", "22": "I2C_SCL", "23": "I2C_SDA",
           "1": "EXPANDER_INT", "4": "SD_CD", "5": "TUSB_OUT1", "6": "TUSB_OUT2", "7": "TUSB_OUT3",
           "8": "CHG_INT", "9": "EXP_PRESENT", "10": "LCD_RST_CTRL", "11": "EXP_CS_N", "13": "SX_NRESET",
           "14": "SD_SW_EN", "15": "AUD_SW_EN", "16": "ADSB_SW_EN", "17": "RP_RUN", "18": "BUCK_PG",
           "19": "EXP_PERIPH_RST", "20": "CHG_EN"},
          mpn="TCA9535PWR", source="TI SCPS201F; port map DIG-03 + one-shot spares")
    d.C("C43", "100nF", "3V3_MAIN")
    d.R("R45", "10k", "EXPANDER_INT", "3V3_MAIN")
    d.R("R46", "100k", "EXP_PRESENT", "3V3_MAIN")
    d.R("R47", "100k", "EXP_CS_N", "3V3_MAIN")
    d.R("R48", "100k", "EXP_PERIPH_RST", "3V3_MAIN")
    d.TP("TP14", "EXPANDER_INT")
    d.g("exp")
    d.add("J2", "Connector_Generic_MountingPin:Conn_01x12_MountingPin", "BM12B-GHS-TBT (expansion)",
          "Connector_JST:JST_GH_BM12B-GHS-TBT_1x12-1MP_P1.25mm_Vertical",
          {"1": "GND", "2": "3V3_EXP", "3": "I2C_SDA", "4": "I2C_SCL", "5": "SPI_SCLK", "6": "GND",
           "7": "SPI_MOSI", "8": "SPI_MISO", "9": "EXP_CS_N", "10": "EXP_UART_TX", "11": "EXP_UART_RX",
           "12": "EXP_IRQ", "MP": "GND"}, mpn="BM12B-GHS-TBT", status="pinout = CONNECTOR_ARCHITECTURE.md; ESD/hot-plug TBD")
    d.C("C44", "10uF", "3V3_EXP", fp="C0603")
    d.flag("3V3_EXP")

    # ======================================================================= 05 display
    d.sheet("05 Display and touch", "05_display.kicad_sch",
            "05 Orient AFY240320A1-2.8INTH-C1: XF3M FPC connectors, 3.3->1.8 V SPI branch, reset, backlight", [
        "Write-only three-line 9-bit SPI, IM2/IM1/IM0 = 1/0/1 (rev J). SN74AXC4T245: DIR high (A->B), OE pulled low (enabled) and driven by GPIO8 LCD_AUX.",
        "TFT reset: TCA9535 P06 LCD_RST_CTRL (100k pull-down) -> SN74LVC1G07 open drain -> 10k to 1V8_LOGIC (DSP-02). Touch RESET shares LCD_RST_CTRL (3.3 V, one-shot proposal).",
        "UNUSED-PIN TIES ARE TBD (gate 3): DB17..DB0, DOTCLK/DE/VSYNC/HSYNC tied to GND; RD/WR tied high through R53/R54 0R (swap to GND if the controller spec requires).",
        "TFT VCC fed from 3V3_MAIN (2.4-3.6 V range) - the VDD/VDDI contradiction in the Orient drawing is still open (O01). Backlight TPS61169: RSET 2.21R -> ~92 mA.",
    ])
    d.g("fpc40")
    fpc = {"1": "LED_K", "2": "LED_A", "3": "GND", "4": "1V8_LOGIC", "5": "GND", "6": "1V8_LOGIC",
           "7": "LCD_SDA_1V8", "8": "GND", "9": "GND", "10": "GND", "11": "GND", "12": "LCD_VCC",
           "13": "LCD_RESET_1V8", "14": "GND", "33": "LCD_RD_TIE", "34": "LCD_WR_TIE", "35": "LCD_SCL_1V8",
           "36": "LCD_CS_1V8", "37": "", "38": "", "39": "", "40": "", "MP": "GND"}
    for p in range(15, 33):
        fpc[str(p)] = "GND"
    d.add("J3", "Connector_Generic_MountingPin:Conn_01x40_MountingPin", "XF3M-4015-1B (TFT 40p FPC)",
          f"{PLIB}:Omron_XF3M-4015-1B_1x40-1MP_P0.5mm_Horizontal", fpc, mpn="XF3M-4015-1B",
          status="SAMPLE/CONTROLLED-DRAWING HOLD (O01); footprint from Omron G146-E1 lands")
    d.R("R49", "0R", "3V3_MAIN", "LCD_VCC", fp="R0603", status="TFT VCC link (O01 power clarification)")
    d.C("C50", "10uF", "LCD_VCC", fp="C0603")
    d.C("C51", "100nF", "LCD_VCC")
    d.R("R53", "0R", "LCD_RD_TIE", "1V8_LOGIC", status="unused RD tie TBD")
    d.R("R54", "0R", "LCD_WR_TIE", "1V8_LOGIC", status="unused WR(D/CX) tie TBD")
    d.g("xlat")
    d.add("U14", f"{PLIB}:SN74AXC4T245PW", "SN74AXC4T245PWR", CUSTOM["SN74AXC4T245PW"]["fp"],
          {"1": "3V3_MAIN", "16": "1V8_LOGIC", "2": "3V3_MAIN", "3": "3V3_MAIN", "15": "LCD_XLT_OE",
           "14": "LCD_XLT_OE", "4": "SPI_SCLK", "5": "SPI_MOSI", "6": "LCD_CS", "7": "GND",
           "13": "LCD_SCL_1V8", "12": "LCD_SDA_1V8", "11": "LCD_CS_1V8", "10": "", "8": "GND", "9": "GND"},
          mpn="SN74AXC4T245PWR", source="TI SCES877B; DSP-02")
    d.R("R50", "10k", "LCD_XLT_OE", "GND")
    d.R("R55", "0R", "LCD_AUX", "LCD_XLT_OE", status="GPIO8 host control of translator OE (optional)")
    d.C("C52", "100nF", "3V3_MAIN")
    d.C("C53", "100nF", "1V8_LOGIC")
    d.g("rst")
    d.add("U15", "74xGxx:74LVC1G07", "SN74LVC1G07DBVR", "Package_TO_SOT_SMD:SOT-23-5",
          {"1": "", "2": "LCD_RST_CTRL", "3": "GND", "4": "LCD_RESET_1V8", "5": "1V8_LOGIC"},
          mpn="SN74LVC1G07DBVR", source="TI SCES296AG 7.4")
    d.R("R51", "100k", "LCD_RST_CTRL", "GND")
    d.R("R52", "10k", "LCD_RESET_1V8", "1V8_LOGIC")
    d.C("C54", "100nF", "1V8_LOGIC")
    d.g("bl")
    d.add("U16", f"{PLIB}:TPS61169", "TPS61169DCKR", CUSTOM["TPS61169"]["fp"],
          {"5": "3V3_MAIN", "4": "LCD_BL_PWM", "1": "BL_SW", "3": "LED_K", "2": "GND"}, mpn="TPS61169DCKR",
          source="TI SNVSA40B")
    d.add("L3", "Device:L", "10uH LPS4018-103MRC", f"{PLIB}:L_Coilcraft_LPS4018",
          {"1": "3V3_MAIN", "2": "BL_SW"}, mpn="LPS4018-103MRC")
    d.add("D1", "Device:D_Schottky", "60V Schottky TBD", "Diode_SMD:D_SOD-123F", {"1": "LED_A", "2": "BL_SW"},
          status="exact 60 V-class part TBD (open)")
    d.C("C55", "4.7uF 10V", "3V3_MAIN", fp="C0603")
    d.C("C56", "1uF 50V X7R", "LED_A", fp="C0805")
    d.R("R56", "2.21R 1% 0.1W", "LED_K", "GND", fp="R0603")
    d.R("R57", "100k", "LCD_BL_PWM", "GND")
    d.g("fpc6")
    d.add("J4", "Connector_Generic_MountingPin:Conn_01x06_MountingPin", "XF3M-0615-1B (CTP 6p FPC)",
          f"{PLIB}:Omron_XF3M-0615-1B_1x06-1MP_P0.5mm_Horizontal",
          {"1": "LCD_RST_CTRL", "2": "3V3_MAIN", "3": "GND", "4": "TOUCH_INT", "5": "I2C_SCL", "6": "I2C_SDA",
           "MP": "GND"}, mpn="XF3M-0615-1B", status="SAMPLE HOLD; ST1633I address 0x70 convention open")
    d.R("R58", "10k", "TOUCH_INT", "3V3_MAIN")
    d.C("C57", "100nF", "3V3_MAIN")

    # ======================================================================= 07 GNSS
    d.sheet("07 GNSS", "07_gnss.kicad_sch", "07 u-blox MAX-M10S-00B, passive antenna U.FL, TPD1E0B04 ESD", [
        "P20/GNSS-01: VCC and V_IO tied to 3V3_GNSS, VIO_SEL open, V_BCKP/RESET_N/EXTINT/LNA_EN/VCC_RF/SDA/SCL/SAFEBOOT_N open.",
        "RF_IN: short 50-ohm GCPW from U.FL (J5) with shunt TPD1E0B04 at the connector. No bias tee (passive FXP611 antenna). Firmware sets AIR4 dynamic model.",
    ])
    d.g("gnss")
    d.add("U17", "RF_GPS:MAX-M10S", "MAX-M10S-00B", f"{PLIB}:u-blox_MAX-M10S-00B_LCC-18_10.1x9.7mm",
          {"1": "GND", "10": "GND", "12": "GND", "2": "GNSS_RX", "3": "GNSS_TX", "4": "GNSS_PPS", "5": "",
           "6": "", "7": "3V3_GNSS", "8": "3V3_GNSS", "9": "", "11": "GNSS_RF", "13": "", "14": "", "15": "",
           "16": "", "17": "", "18": ""}, mpn="MAX-M10S-00B", status="LOCKED", source="u-blox UBX-22035176 R08")
    d.C("C60", "1uF X7R", "3V3_GNSS")
    d.C("C61", "100nF", "3V3_GNSS")
    d.add("J5", "Connector:Conn_Coaxial", "U.FL-R-SMT-1(60) GNSS", f"{PLIB}:Hirose_U.FL-R-SMT-1_60_Vertical",
          {"1": "GNSS_RF", "2": "GND"}, mpn="U.FL-R-SMT-1(60)")
    d.add("D2", f"{PLIB}:TPD1E0B04", "TPD1E0B04DPYR", CUSTOM["TPD1E0B04"]["fp"], {"1": "GNSS_RF", "2": "GND"},
          mpn="TPD1E0B04DPYR")
    d.TP("TP15", "GNSS_PPS")
    d.TP("TP16", "GNSS_RX")
    d.flag("3V3_GNSS")

    # ======================================================================= 06 sensors
    d.sheet("06 Sensors", "06_sensors.kicad_sch", "06 ICM-42688-P, MMC5983MA, BMP581, SHT40 on the shared 100 kHz I2C bus", [
        "Addresses: ICM-42688-P 0x68 (AD0=GND), MMC5983MA 0x30, BMP581 0x46 (SDO=GND, CSB=VDDIO), SHT40-AD1B 0x44. All on 3V3_MAIN.",
        "Placement (SNS-02): IMU near centroid >=3 mm from anchors; MMC >=15 mm from cells/inductors; BMP581+SHT40 at the top vent edge, no copper/vias under BMP581, SHT40 on a slotted thermal tab.",
        "BMP581 INT tied to GND with interrupts disabled (repo 04_sensors sheet); MMC INT and ICM INT2 unused (polled/NC).",
    ])
    d.g("imu")
    d.add("U30", f"{PLIB}:ICM-42688-P", "ICM-42688-P", CUSTOM["ICM-42688-P"]["fp"],
          {"8": "3V3_MAIN", "5": "3V3_MAIN", "14": "I2C_SDA", "13": "I2C_SCL", "12": "3V3_MAIN", "1": "GND",
           "4": "IMU_INT1", "9": "", "2": "GND", "3": "GND", "10": "GND", "11": "GND", "7": "GND", "6": "GND"},
          mpn="ICM-42688-P", status="LOCKED - assembler mask/paste gate", source="TDK DS-000347 v1.9")
    d.C("C30", "100nF", "3V3_MAIN")
    d.C("C31", "2.2uF", "3V3_MAIN")
    d.C("C32", "10nF", "3V3_MAIN", status="VDDIO decoupling (DS)")
    d.g("mag")
    d.add("U31", f"{PLIB}:MMC5983MA", "MMC5983MA", CUSTOM["MMC5983MA"]["fp"],
          {"2": "3V3_MAIN", "13": "3V3_MAIN", "16": "I2C_SDA", "1": "I2C_SCL", "4": "3V3_MAIN", "5": "",
           "15": "", "10": "MAG_CAP", "3": "", "6": "", "7": "", "8": "", "12": "", "14": "", "9": "GND", "11": "GND"},
          mpn="MMC5983MA", status="LOCKED - magnetic placement review", source="MEMSIC MMC5983MA Rev A")
    d.C("C33", "10uF", "MAG_CAP", fp="C0603", status="SET/RESET capacitor per DS")
    d.C("C34", "1uF", "3V3_MAIN")
    d.g("baro")
    d.add("U32", f"{PLIB}:BMP581", "BMP581", CUSTOM["BMP581"]["fp"],
          {"10": "3V3_MAIN", "1": "3V3_MAIN", "4": "I2C_SDA", "2": "I2C_SCL", "6": "3V3_MAIN", "5": "GND",
           "7": "GND", "3": "GND", "8": "GND", "9": "GND"}, mpn="BMP581", status="LOCKED (D29 indicative backup)",
          source="Bosch BST-BMP581-DS004-13")
    d.C("C35", "100nF", "3V3_MAIN")
    d.C("C36", "100nF", "3V3_MAIN")
    d.g("rh")
    d.add("U33", "Sensor_Humidity:SHT4x", "SHT40-AD1B-R2", f"{PLIB}:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad",
          {"1": "I2C_SDA", "2": "I2C_SCL", "3": "3V3_MAIN", "4": "GND"}, mpn="SHT40-AD1B-R2", status="LOCKED",
          source="Sensirion SHT4x v7.3")
    d.C("C37", "100nF", "3V3_MAIN")

    # ======================================================================= 08 LoRa
    d.sheet("08 LoRa SX1262", "08_lora.kicad_sch", "08 Semtech SX1262 (DC-DC, 32 MHz crystal), PE4259 switch, U.FL", [
        "Topology per Semtech AN1200.40 Rev 1.1 Fig.5 (E428) / E449: VDD_IN+VBAT+VBAT_IO on 3V3_MAIN, 15uH DCC_SW-VREG (DC-DC), 470nF/100nF/10uF supply, DIO2 -> 100R/1nF -> PE4259 CTRL.",
        "*** ALL TX match/harmonic filter and RX balun VALUES ARE TBD: AN1200.40 prints designators only. Take exact values from the native E449 regional BOM and re-tune on this stackup (AGENTS rule 5). ***",
        "32 MHz crystal MPN TBD (CL 10 pF, ESR <=60R per SX1261/2 DS Rev 1.2). DIO3 left open (TCXO fallback). No TX before a regional configuration (AGENTS rule 14).",
    ])
    d.g("sx")
    d.add("U40", "RF:SX1262IMLTRT", "SX1262IMLTRT", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
          {"1": "3V3_MAIN", "10": "3V3_MAIN", "11": "3V3_MAIN", "2": "GND", "5": "GND", "8": "GND", "20": "GND", "25": "GND",
           "3": "SX_XTA", "4": "SX_XTB", "6": "", "7": "SX_VREG", "9": "SX_DCC_SW", "12": "SX_DIO2", "13": "SX_DIO1",
           "14": "SX_BUSY", "15": "SX_NRESET", "16": "SPI_MISO", "17": "SPI_MOSI", "18": "SPI_SCLK", "19": "SX_NSS",
           "21": "LORA_RFI_P", "22": "LORA_RFI_N", "23": "LORA_RFO", "24": "SX_VR_PA"},
          mpn="SX1262IMLTRT", status="LOCKED", source="Semtech SX1261/2 DS Rev 1.2; EP numbered 25 in KiCad (pin 0 in DS)")
    d.C("C70", "10uF", "3V3_MAIN", fp="C0603")
    d.C("C71", "470nF", "3V3_MAIN")
    d.C("C72", "100nF", "3V3_MAIN")
    d.add("L70", "Device:L", "15uH (DC-DC)", "Inductor_SMD:L_0805_2012Metric", {"1": "SX_DCC_SW", "2": "SX_VREG"},
          status="AN1200.40 L7 15uH; exact part/ISAT TBD")
    d.C("C73", "470nF", "SX_VREG", status="VREG decoupling; value per E449 BOM TBD")
    d.add("Y2", "Device:Crystal_GND24", "32 MHz (CL 10pF) MPN TBD", "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm",
          {"1": "SX_XTA", "3": "SX_XTB", "2": "GND", "4": "GND"}, status="MPN TBD")
    d.R("R70", "100k", "SX_NRESET", "3V3_MAIN", status="P10 default released")
    d.g("sxrf")
    d.add("L71", "Device:L", "TBD (E449)", "Inductor_SMD:L_0402_1005Metric", {"1": "SX_VR_PA", "2": "LORA_RFO"},
          status="PA supply choke VR_PA->RFO; value TBD")
    d.C("C74", "TBD (E449)", "SX_VR_PA", status="VR_PA decoupling; value TBD")
    d.C("C75", "TBD (E449)", "LORA_RFO", status="TX match shunt; value TBD")
    d.add("L72", "Device:L", "TBD (E449)", "Inductor_SMD:L_0402_1005Metric", {"1": "LORA_RFO", "2": "LORA_TXF1"},
          status="TX match/notch series; value TBD")
    d.C("C76", "TBD (E449)", "LORA_TXF1", status="pi-filter shunt; value TBD")
    d.add("L73", "Device:L", "TBD (E449)", "Inductor_SMD:L_0402_1005Metric", {"1": "LORA_TXF1", "2": "LORA_TXF2"},
          status="pi-filter series; value TBD")
    d.C("C77", "TBD (E449)", "LORA_TXF2", status="pi-filter shunt; value TBD")
    d.C("C78", "TBD (E449)", "LORA_TXF2", "LORA_TX_SW", status="DC block to PE4259 RF1; value TBD")
    d.C("C79", "TBD (E449)", "LORA_RX_SW", "LORA_RFI_P", status="RX balun series C; value TBD")
    d.add("L74", "Device:L", "TBD (E449)", "Inductor_SMD:L_0402_1005Metric", {"1": "LORA_RX_SW", "2": "LORA_RFI_N"},
          status="RX balun series L; value TBD")
    d.C("C80", "TBD (E449)", "LORA_RFI_N", status="RX balun shunt; value TBD")
    d.g("sw")
    d.add("U41", f"{PLIB}:PE4259", "PE4259", CUSTOM["PE4259"]["fp"],
          {"5": "LORA_RFC", "4": "LORA_SW_CTRL", "6": "LORA_SW_VDD", "1": "LORA_TX_SW", "3": "LORA_RX_SW", "2": "GND"},
          mpn="PE4259", status="PROPOSED (AN1200.40 reference switch); RF1/RF2 vs CTRL polarity to confirm in firmware",
          source="pSemi DOC-03694")
    d.R("R71", "100R", "SX_DIO2", "LORA_SW_CTRL", status="AN1200.40 R3")
    d.C("C81", "1nF", "LORA_SW_CTRL", status="AN1200.40 C15")
    d.R("R72", "100R", "3V3_MAIN", "LORA_SW_VDD", status="AN1200.40 R4")
    d.C("C82", "1nF", "LORA_SW_VDD", status="AN1200.40 C14")
    d.C("C83", "TBD (E449)", "LORA_RFC", "LORA_ANT", status="antenna DC block; value TBD")
    d.add("J6", "Connector:Conn_Coaxial", "U.FL-R-SMT-1(60) LoRa", f"{PLIB}:Hirose_U.FL-R-SMT-1_60_Vertical",
          {"1": "LORA_ANT", "2": "GND"}, mpn="U.FL-R-SMT-1(60)")

    # ======================================================================= 09 ADS-B
    d.sheet("09 ADS-B receiver", "09_adsb.kicad_sch", "09 1090 MHz chain (BLB01 x2, TA2003A x2, ADL5513, MCP6566) and RP2040 capture", [
        "Chain per docs/ADSB_VALIDATION.md. BLB01 bias per BeRex rev 6.6 evaluation BOM (C1 100pF in, C2 12pF out, R1 6.8k/C3 12pF/L1 27nH Ven, R2 0R/C4 100pF/L2 82nH Vd).",
        "ADL5513 measurement mode (VSET=VOUT), 52.3R input termination, 47nF coupling. TADJ resistor and CLPF (1 nF basic value is too slow for 0.5 us pulses) are TBD/bench items.",
        "MCP6566T-E/OT base pin map, 2.2k pull-up to the RP2040 bank; threshold divider R86/R87 BLOCKED by OWN-09 (value TBD). R88/C88 DNP option: RP2040 PWM threshold.",
        "RP2040 per DIG-01 (Raspberry Pi minimal design): 12 MHz ABM8-272-T3 + 1k XOUT, 15pF loads; QSPI_SS 1k to USB_BOOT pad; RUN 10k/100nF + TCA9535 P14. Domain 3V3_ADSB switched (P13).",
        "UART0: GPIO0 TX -> RP_UART_RX, GPIO1 RX <- RP_UART_TX, GPIO2 CTS <- RP_UART_RTS, GPIO3 RTS -> RP_UART_CTS (one-shot pin choice). Back-power of ESP32-driven lines into an OFF RP2040 is an open SYS-02 item.",
    ])
    d.g("adsbsw")
    d.add("U11", f"{PLIB}:TPS22918", "TPS22918DBVR", CUSTOM["TPS22918"]["fp"],
          {"1": "3V3_MAIN", "3": "ADSB_SW_EN", "4": "ADSB_CT", "6": "3V3_ADSB", "5": "3V3_ADSB", "2": "GND"},
          mpn="TPS22918DBVR", source="TI SLVSD76C")
    d.R("R90", "100k", "ADSB_SW_EN", "GND", status="default OFF (DIG-03)")
    d.C("C90", "100pF", "ADSB_CT")
    d.C("C91", "10uF", "3V3_ADSB", fp="C0603")
    d.TP("TP20", "3V3_ADSB")
    d.g("rp")
    rp = {str(n): "3V3_ADSB" for n in (1, 10, 22, 33, 42, 49, 43, 44, 48)}
    rp.update({"23": "1V1_ADSB", "50": "1V1_ADSB", "45": "1V1_ADSB", "57": "GND", "19": "GND",
               "20": "RP_XIN", "21": "RP_XOUT", "24": "RP_SWCLK", "25": "RP_SWDIO", "26": "RP_RUN",
               "2": "RP_UART_RX", "3": "RP_UART_TX", "4": "RP_UART_RTS", "5": "RP_UART_CTS",
               "11": "ADSB_PULSE", "12": "ADSB_THR_PWM",
               "51": "QSPI_SD3", "52": "QSPI_SCLK", "53": "QSPI_SD0", "54": "QSPI_SD2", "55": "QSPI_SD1", "56": "QSPI_SS",
               "46": "", "47": ""})
    for n in (6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41):
        rp[str(n)] = ""
    d.add("U20", "MCU_RaspberryPi:RP2040", "RP2040", "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm", rp,
          mpn="RP2040", status="LOCKED", source="RP2040 datasheet + Hardware design with RP2040")
    for i in range(6):
        d.C(f"C{100 + i}", "100nF", "3V3_ADSB")
    d.C("C106", "100nF", "3V3_ADSB", status="ADC_AVDD")
    d.C("C107", "100nF", "3V3_ADSB", status="USB_VDD")
    d.C("C108", "1uF", "3V3_ADSB", status="VREG_VIN")
    d.C("C109", "1uF", "1V1_ADSB", status="VREG_VOUT")
    d.C("C110", "100nF", "1V1_ADSB")
    d.C("C111", "100nF", "1V1_ADSB")
    d.R("R91", "10k", "RP_RUN", "3V3_ADSB")
    d.C("C112", "100nF", "RP_RUN")
    d.R("R92", "1k", "QSPI_SS", "USB_BOOT", status="BOOTSEL strap (DIG-01)")
    d.TP("TP21", "USB_BOOT")
    d.TP("TP22", "RP_RUN")
    d.TP("TP23", "RP_SWCLK")
    d.TP("TP24", "RP_SWDIO")
    d.flag("ADSB_DET_VP")
    d.add("U21", "Memory_Flash:W25Q128JVS", "W25Q128JVSIQ", f"{PLIB}:Winbond_W25Q128JVSIQ_SOIC-8_5.3x5.3mm_P1.27mm",
          {"1": "QSPI_SS", "2": "QSPI_SD1", "3": "QSPI_SD2", "4": "GND", "5": "QSPI_SD0", "6": "QSPI_SCLK",
           "7": "QSPI_SD3", "8": "3V3_ADSB"}, mpn="W25Q128JVSIQ", source="Winbond Rev M")
    d.C("C113", "100nF", "3V3_ADSB")
    d.add("Y1", "Device:Crystal_GND24", "12MHz ABM8-272-T3", f"{PLIB}:Abracon_ABM8-272-T3_Crystal_SMD_3225-4Pin_3.2x2.5mm",
          {"1": "RP_XIN", "3": "RP_XTAL_R", "2": "GND", "4": "GND"}, mpn="ABM8-272-T3")
    d.R("R93", "1k", "RP_XOUT", "RP_XTAL_R")
    d.C("C114", "15pF C0G", "RP_XIN")
    d.C("C115", "15pF C0G", "RP_XTAL_R")
    d.g("rf1")
    d.add("J7", "Connector:Conn_Coaxial", "U.FL-R-SMT-1(60) ADS-B", f"{PLIB}:Hirose_U.FL-R-SMT-1_60_Vertical",
          {"1": "ADSB_ANT", "2": "GND"}, mpn="U.FL-R-SMT-1(60)")
    d.add("D3", f"{PLIB}:TPD1E0B04", "TPD1E0B04DPYR (option)", CUSTOM["TPD1E0B04"]["fp"], {"1": "ADSB_ANT", "2": "GND"},
          dnp=True, status="ESD option at ADS-B input - DNP until RF review")
    lna = [("U50", "ADSB_ANT", "ADSB_L1_IN", "ADSB_L1_OUT", "ADSB_L1_BIAS", "ADSB_L1_VEN", "ADSB_L1_VD", "ADSB_S1_IN", 80),
           ("U52", "ADSB_S1_OUT", "ADSB_L2_IN", "ADSB_L2_OUT", "ADSB_L2_BIAS", "ADSB_L2_VEN", "ADSB_L2_VD", "ADSB_S2_IN", 84)]
    for ref, src, rin, out, bias, ven, vd, nxt, k in lna:
        d.C(f"C{k}0", "100pF", src, rin, status="BLB01 EVB C1")
        d.add(ref, f"{PLIB}:BLB01", "BLB01", CUSTOM["BLB01"]["fp"],
              {"2": rin, "1": ven, "7": out, "3": "", "4": "", "5": "", "6": "", "8": "", "9": "GND"},
              mpn="BLB01", status="PROPOSED - prototype required", source="BeRex BLB01 rev 6.6")
        d.R(f"R{k}0", "6.8k", "3V0_RF_QUIET", bias, status="BLB01 EVB R1")
        d.C(f"C{k}1", "12pF", bias, status="BLB01 EVB C3")
        d.add(f"L{k}0", "Device:L", "27nH", "Inductor_SMD:L_0603_1608Metric", {"1": bias, "2": ven}, status="BLB01 EVB L1")
        d.R(f"R{k}1", "0R", "3V0_RF_QUIET", vd, status="BLB01 EVB R2")
        d.C(f"C{k}2", "100pF", vd, status="BLB01 EVB C4")
        d.add(f"L{k}1", "Device:L", "82nH", "Inductor_SMD:L_0603_1608Metric", {"1": vd, "2": out}, status="BLB01 EVB L2")
        d.C(f"C{k}3", "12pF", out, nxt, status="BLB01 EVB C2 (RF out)")
    d.add("FL1", f"{PLIB}:TA2003A", "TA2003A 1090MHz SAW", CUSTOM["TA2003A"]["fp"],
          {"B": "ADSB_S1_IN", "E": "ADSB_S1_OUT", "A": "GND", "C": "GND", "D": "GND", "F": "GND"}, mpn="TA2003A")
    d.add("FL2", f"{PLIB}:TA2003A", "TA2003A 1090MHz SAW", CUSTOM["TA2003A"]["fp"],
          {"B": "ADSB_S2_IN", "E": "ADSB_DET_IN", "A": "GND", "C": "GND", "D": "GND", "F": "GND"}, mpn="TA2003A")
    d.g("det")
    d.add("U54", f"{PLIB}:ADL5513", "ADL5513ACPZ-R7", CUSTOM["ADL5513"]["fp"],
          {"1": "ADSB_DET_VP", "4": "ADSB_DET_VP", "2": "ADSB_INHI", "3": "ADSB_INLO", "9": "ADSB_TADJ",
           "14": "ADSB_CLPF", "12": "ADSB_VIDEO", "11": "ADSB_VIDEO", "10": "GND", "17": "GND",
           "5": "", "6": "", "7": "", "8": "", "13": "", "15": "", "16": ""},
          mpn="ADL5513ACPZ-R7", status="PROPOSED - EP land TBD (CP-16-22)", source="ADI ADL5513 Rev B")
    d.R("R95", "52.3R 1%", "ADSB_DET_IN", "GND", status="ADI basic connections R1")
    d.C("C95", "47nF", "ADSB_DET_IN", "ADSB_INHI")
    d.C("C96", "47nF", "ADSB_INLO", "GND")
    d.R("R96", "0R", "3V0_RF_QUIET", "ADSB_DET_VP")
    d.C("C97", "100nF", "ADSB_DET_VP")
    d.C("C98", "100pF", "ADSB_DET_VP")
    d.R("R97", "TBD (TADJ @1090 MHz)", "ADSB_TADJ", "GND", status="value from ADI TADJ table TBD")
    d.C("C99", "1nF", "ADSB_CLPF", dnp=True, status="basic value 1nF slows pulses; DNP pending bench")
    d.g("cmp")
    d.add("U55", "Comparator:MCP6566", "MCP6566T-E/OT", "Package_TO_SOT_SMD:SOT-23-5",
          {"1": "ADSB_PULSE", "2": "GND", "3": "ADSB_VIDEO", "4": "ADSB_THR", "5": "3V0_RF_QUIET"},
          mpn="MCP6566T-E/OT", source="Microchip DS20002143G base map")
    d.C("C116", "100nF", "3V0_RF_QUIET")
    d.R("R98", "2.2k 1%", "ADSB_PULSE", "3V3_ADSB", status="ADSB-01")
    d.R("R86", "TBD (OWN-09)", "3V0_RF_QUIET", "ADSB_THR", status="threshold divider BLOCKED by OWN-09")
    d.R("R87", "TBD (OWN-09)", "ADSB_THR", "GND", status="threshold divider BLOCKED by OWN-09")
    d.R("R88", "10k", "ADSB_THR_PWM", "ADSB_THR", dnp=True, status="optional RP2040 PWM threshold")
    d.C("C88", "100nF", "ADSB_THR", dnp=True)
    d.TP("TP25", "ADSB_VIDEO")
    d.TP("TP26", "ADSB_PULSE")

    # ======================================================================= 10 storage + audio
    d.sheet("10 Storage and audio", "10_storage_audio.kicad_sch", "10 microSD (DM3AT) on switched 3V3_SD; T5838 PDM mic on 1V8_AUDIO_SW", [
        "DIG-02: SPI mode (DAT3 = SD_CS), 10k pull-ups on CMD/DAT0/DAT3 to 3V3_SD (never 3V3_MAIN), no CLK pull-up, card detect 100k to 3V3_MAIN on TCA P00, TPD4E05U06 at the socket.",
        "AUD-01/AUD-02: 1V8_AUDIO_SW = TPS22918 branch from 1V8_LOGIC (AUD_SW_EN, pull-down). TXU0202 A1->B1Y clock, B2->A2Y data, OE 100k to 1V8_AUDIO_SW.",
        "T5838 SELECT=GND (DATA1/right), THSEL=GND and WAKE open (no AAD). 0.8 mm sound hole in the footprint, no paste on the port.",
    ])
    d.g("sdsw")
    d.add("U10", f"{PLIB}:TPS22918", "TPS22918DBVR", CUSTOM["TPS22918"]["fp"],
          {"1": "3V3_MAIN", "3": "SD_SW_EN", "4": "SD_CT", "6": "3V3_SD", "5": "3V3_SD", "2": "GND"}, mpn="TPS22918DBVR")
    d.R("R100", "100k", "SD_SW_EN", "GND", status="default OFF")
    d.C("C120", "100pF", "SD_CT")
    d.C("C121", "10uF", "3V3_SD", fp="C0603")
    d.C("C122", "100nF", "3V3_SD")
    d.TP("TP27", "3V3_SD")
    d.g("sd")
    d.add("J8", "Connector:Micro_SD_Card_Det_Hirose_DM3AT", "DM3AT-SF-PEJM5", f"{PLIB}:Hirose_DM3AT-SF-PEJM5_microSD_HC",
          {"1": "", "2": "SD_CS", "3": "SPI_MOSI", "4": "3V3_SD", "5": "SPI_SCLK", "6": "GND", "7": "SPI_MISO",
           "8": "", "9": "SD_CD", "10": "GND", "SH": "GND"}, mpn="DM3AT-SF-PEJM5", source="Hirose drawing 0000947170 Rev 4")
    d.R("R101", "10k", "SD_CS", "3V3_SD")
    d.R("R102", "10k", "SPI_MOSI", "3V3_SD")
    d.R("R103", "10k", "SPI_MISO", "3V3_SD")
    d.R("R104", "100k", "SD_CD", "3V3_MAIN")
    d.add("U23", "Power_Protection:TPD4E05U06DQA", "TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
          {"1": "SPI_SCLK", "2": "SPI_MOSI", "4": "SPI_MISO", "5": "SD_CS", "3": "GND", "8": "GND",
           "6": "", "7": "", "9": "", "10": ""}, mpn="TPD4E05U06DQARG4")
    d.TP("TP28", "SD_CD")
    d.g("audsw")
    d.add("U12", f"{PLIB}:TPS22918", "TPS22918DBVR", CUSTOM["TPS22918"]["fp"],
          {"1": "1V8_LOGIC", "3": "AUD_SW_EN", "4": "AUD_CT", "6": "1V8_AUDIO_SW", "5": "1V8_AUDIO_SW", "2": "GND"},
          mpn="TPS22918DBVR", status="AUD-02 proposed branch; CT/QOD/ramp review open")
    d.R("R105", "100k", "AUD_SW_EN", "GND", status="default OFF")
    d.C("C123", "100pF", "AUD_CT")
    d.C("C124", "1uF", "1V8_AUDIO_SW")
    d.g("aud")
    d.add("U24", f"{PLIB}:TXU0202DCU", "TXU0202DCUR", CUSTOM["TXU0202DCU"]["fp"],
          {"3": "3V3_MAIN", "7": "1V8_AUDIO_SW", "5": "PDM_CLK", "4": "PDM_DATA", "6": "PDM_OE", "8": "PDM_CLK_1V8",
           "1": "PDM_DATA_1V8", "2": "GND"}, mpn="TXU0202DCUR", source="TI SCES942A (DCU = VSSOP-8 2.3x2.0 mm)")
    d.R("R106", "100k", "PDM_OE", "1V8_AUDIO_SW")
    d.C("C125", "100nF", "3V3_MAIN")
    d.C("C126", "100nF", "1V8_AUDIO_SW")
    d.add("MK1", f"{PLIB}:T5838", "MMICT5838-00-012", CUSTOM["T5838"]["fp"],
          {"7": "1V8_AUDIO_SW", "6": "PDM_CLK_1V8", "2": "GND", "5": "GND", "1": "PDM_DATA_1V8", "4": "", "3": "GND"},
          mpn="MMICT5838-00-012", status="PREFERRED CANDIDATE - acoustic/footprint review")
    d.C("C127", "100nF X7R", "1V8_AUDIO_SW", status="DS: 0.1uF at pin 7")

    # ======================================================================= 11 mechanical
    d.sheet("11 Mechanical", "11_mechanical.kicad_sch", "11 Mounting holes, fiducials", [
        "Three M2.5 mounting holes in the left strip (the 2S holder covers the back for x > 14.7 mm; holder is fixed to the rear shell); three fiducials.",
    ])
    d.g("mech")
    for i in range(3):
        d.add(f"H{i + 1}", "Mechanical:MountingHole", "M2.5", "MountingHole:MountingHole_2.7mm_M2.5", {})
    for i in range(3):
        d.add(f"FID{i + 1}", "Mechanical:Fiducial", "Fiducial", "Fiducial:Fiducial_1mm_Mask2mm", {})

    return d
