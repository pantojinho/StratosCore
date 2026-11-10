"""Quantitative layout audit: per-net track stats and key distances."""
import sys, math, pcbnew, collections
b=pcbnew.LoadBoard(sys.argv[1]); MM=pcbnew.ToMM
stats=collections.defaultdict(lambda: dict(len=collections.Counter(), wmin=1e9, wmax=0, vias=0))
for t in b.GetTracks():
    n=t.GetNetname()
    if t.GetClass()=='PCB_VIA': stats[n]['vias']+=1; continue
    L=MM(t.GetLength()); w=MM(t.GetWidth()); s=stats[n]
    s['len'][b.GetLayerName(t.GetLayer())]+=L; s['wmin']=min(s['wmin'],w); s['wmax']=max(s['wmax'],w)
def show(prefixes):
    for n in sorted(stats):
        if any(n.split('/')[-1].startswith(p) for p in prefixes):
            s=stats[n]; print(f"  {n:22} total {sum(s['len'].values()):6.1f} mm  w {s['wmin']:.2f}-{s['wmax']:.2f}  vias {s['vias']:2d}  "+' '.join(f"{k}:{v:.1f}" for k,v in s['len'].items()))
print('POWER nets'); show(['VBUS','PACK_P','BAT_','CHG_SW','CHG_PMID','CHG_SNS','CHG_BTST','CHG_REGN','BUCK_SW','3V3_','1V8','3V0','BL_SW','LED_','PROT_DRAIN','1V1'])
print('RF nets'); show(['GNSS_RF','ADSB_ANT','ADSB_L','ADSB_S','ADSB_DET_IN','ADSB_INHI','LORA_','SX_X','SX_DCC','SX_VREG','SX_VR'])
print('USB / clocks'); show(['USB_D','RP_X','QSPI','SPI_','PDM_','ADSB_PULSE','ADSB_VIDEO'])
def pad(ref,num):
    f=b.FindFootprintByReference(ref)
    for p in f.Pads():
        if p.GetNumber()==num: return p
def dist(a,b_): 
    pa,pb=pad(*a).GetPosition(),pad(*b_).GetPosition(); return math.hypot(MM(pa.x-pb.x),MM(pa.y-pb.y))
print('KEY DISTANCES (pad centre to pad centre, mm)')
for name,a,c in [('buck Cin C20.1 -> U7.12 PVIN',('C20','1'),('U7','12')),('buck Cin C20.2 -> U7.15 PGND',('C20','2'),('U7','15')),('buck L2.1 -> U7.2 SW',('L2','1'),('U7','2')),('buck Cout C22.1 -> L2.2',('C22','1'),('L2','2')),
    ('chg L1.2 -> U6.17 SW',('L1','2'),('U6','17')),('chg C14.1 SNS -> U6.15',('C14','1'),('U6','15')),('chg C15.1 SNS -> U6.16',('C15','1'),('U6','16')),('chg C11.1 PMID -> U6.21',('C11','1'),('U6','21')),('chg C12 BTST -> U6.12',('C12','1'),('U6','12')),('chg C13 REGN -> U6.11',('C13','1'),('U6','11')),('chg C16 BAT -> U6.13',('C16','1'),('U6','13')),('chg C10 VBUS -> U6.23',('C10','1'),('U6','23')),
    ('BL L3.2 -> U16.1 SW',('L3','2'),('U16','1')),('BL D1.2 -> U16.1',('D1','2'),('U16','1')),('BL C56.1 -> D1.1',('C56','1'),('D1','1')),('BL C55 -> U16.5',('C55','1'),('U16','5')),
    ('ESP C42 -> U1.2',('C42','1'),('U1','2')),('ESP C41 -> U1.2',('C41','1'),('U1','2')),('SX C72 -> U40.10',('C72','1'),('U40','10')),('SX C71 -> U40.1',('C71','1'),('U40','1')),('SX C73 -> U40.7',('C73','1'),('U40','7')),('SX L70.1 -> U40.9',('L70','1'),('U40','9')),('SX Y2.1 -> U40.3',('Y2','1'),('U40','3')),
    ('RP Y1.1 -> U20.20',('Y1','1'),('U20','20')),('RP C109 VREG_VOUT -> U20.45',('C109','1'),('U20','45')),('RP C108 -> U20.44',('C108','1'),('U20','44')),('GNSS C61 -> U17.8',('C61','1'),('U17','8')),('GNSS J5.1 -> U17.11',('J5','1'),('U17','11')),
    ('IMU C30 -> U30.8',('C30','1'),('U30','8')),('MAG C33 -> U31.10',('C33','1'),('U31','10')),('eFuse C1 -> U3.5',('C1','1'),('U3','5')),('eFuse C2 -> U3.6',('C2','1'),('U3','6')),('USB U2.1 -> J1.A6',('U2','1'),('J1','A6')),('MAG U31 -> L2',('U31','2'),('L2','1')),('MAG U31 -> L1',('U31','2'),('L1','1')),('MAG U31 -> L3',('U31','2'),('L3','1')),('BARO U32 -> L3',('U32','1'),('L3','1')),('SHT U33 -> U1.1',('U33','1'),('U1','1'))]:
    try: print(f"  {name:34} {dist(a,c):5.1f}")
    except Exception as e: print('  ',name,'ERR',e)
