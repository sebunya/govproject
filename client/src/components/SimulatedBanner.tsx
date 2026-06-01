interface SimulatedBannerProps {
  service: 'NIRA' | 'URA';
}

const bannerText: Record<string, string> = {
  NIRA: '⚠ SIMULATED: NIRA identity check via UGHub-pattern API. Production calls require a Data Sharing Agreement via NITA-U.',
  URA: '⚠ SIMULATED: URA Tax Clearance via UGHub-pattern API. Production calls require URA system integration via NITA-U.',
};

export default function SimulatedBanner({ service }: SimulatedBannerProps) {
  return (
    <div className="simulated-banner">
      <span className="text-gold-500 text-base mt-0.5 shrink-0">⚠</span>
      <div>
        <span className="font-bold text-yellow-800">SIMULATED INTEGRATION — {service}</span>
        <p className="text-yellow-800 mt-0.5">{bannerText[service]}</p>
      </div>
    </div>
  );
}
