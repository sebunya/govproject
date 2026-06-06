interface PermitCertificateProps {
  app: any;
  onClose: () => void;
}

export default function PermitCertificate({ app, onClose }: PermitCertificateProps) {
  const isTrading = app.serviceCode === 'trading-licence';
  const entityName = isTrading ? (app.businessName || app.cooperativeName) : app.cooperativeName;
  const permitNumber = `MDLG-${app.serviceCode === 'trading-licence' ? 'TL' : 'AP'}-${app.referenceNumber.replace('NGS-', '')}`;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4 print:static print:bg-white">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto print:shadow-none print:max-h-none print:rounded-none" id="permit-print">

        <div className="flex justify-between items-center p-4 border-b print:hidden">
          <h2 className="font-bold text-navy-700">Permit Certificate</h2>
          <div className="flex gap-2">
            <button onClick={() => window.print()} className="btn-secondary text-sm py-1.5">🖨 Print</button>
            <button onClick={onClose} className="btn-secondary text-sm py-1.5">✕ Close</button>
          </div>
        </div>

        <div className="p-8 space-y-6">
          <div className="text-center border-b-4 border-double border-navy-700 pb-6">
            <div className="flex items-center justify-center gap-4 mb-4">
              <div className="w-16 h-16 bg-navy-700 rounded-full flex items-center justify-center text-white text-2xl font-extrabold">🇺🇬</div>
              <div className="text-center">
                <div className="text-xs font-bold text-gray-500 uppercase tracking-widest">Republic of Uganda</div>
                <div className="text-lg font-extrabold text-navy-700">Mbarara District Local Government</div>
                <div className="text-xs text-gray-500">District Agricultural Office</div>
              </div>
              <div className="w-16 h-16 rounded-full overflow-hidden border-4 border-gray-200 flex flex-col items-center justify-center bg-navy-700">
                <span className="text-gold-500 text-3xl font-extrabold leading-none">N</span>
                <div className="flex w-full mt-1" style={{height:'5px'}}>
                  <div className="flex-1 bg-navy-900"/><div className="flex-1 bg-gold-500"/><div className="flex-1 bg-ug-red"/>
                </div>
              </div>
            </div>
            <h1 className="text-2xl font-extrabold text-navy-700 uppercase tracking-wide">
              {isTrading ? 'Trading Licence' : 'Agribusiness Operating Permit'}
            </h1>
            <p className="text-xs text-gray-500 mt-1 uppercase tracking-widest">Certificate of Authorisation</p>
          </div>

          <div className="text-center space-y-4">
            <p className="text-sm text-gray-600">This is to certify that</p>
            <div className="bg-navy-50 rounded-xl p-4">
              <p className="text-2xl font-extrabold text-navy-700">{app.fullName}</p>
              {entityName && <p className="text-lg font-bold text-gray-700 mt-1">({entityName})</p>}
            </div>
            <p className="text-sm text-gray-600">
              of <strong>{app.district} District</strong>, having satisfied all statutory requirements, is hereby authorised to
            </p>
            <div className="bg-gold-50 border-2 border-gold-500 rounded-xl p-4">
              <p className="text-lg font-bold text-navy-700">
                {isTrading
                  ? 'Carry on trading business within the jurisdiction of Mbarara District'
                  : 'Register and operate a cooperative society and conduct agribusiness within Mbarara District'}
              </p>
            </div>
            <p className="text-sm text-gray-600">under the provisions of the {isTrading ? 'Trading Licences Act, Cap 101' : 'Cooperatives Societies Act, Cap 112'} of the Laws of Uganda.</p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm border-t border-b border-gray-200 py-4">
            <div><span className="text-xs text-gray-500 block">Permit Number</span><span className="font-mono font-bold text-navy-700">{permitNumber}</span></div>
            <div><span className="text-xs text-gray-500 block">Reference Number</span><span className="font-mono font-bold">{app.referenceNumber}</span></div>
            <div><span className="text-xs text-gray-500 block">NIN</span><span className="font-mono font-bold">{app.nin}</span></div>
            <div><span className="text-xs text-gray-500 block">TIN</span><span className="font-mono font-bold">{app.proposedTin}</span></div>
            <div><span className="text-xs text-gray-500 block">Issue Date</span><span className="font-bold">{new Date(app.resolvedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div>
            <div><span className="text-xs text-gray-500 block">Valid Until</span><span className="font-bold text-status-green">{new Date(new Date(app.resolvedAt).getTime() + 365 * 86400000).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}</span></div>
          </div>

          <div className="grid grid-cols-2 gap-8 pt-4">
            <div className="text-center">
              <div className="h-12 border-b-2 border-navy-700 mb-2" />
              <p className="text-xs font-bold text-navy-700">Tumusiime Robert</p>
              <p className="text-xs text-gray-500">District Agricultural Officer</p>
              <p className="text-xs text-gray-500">Mbarara District Local Government</p>
            </div>
            <div className="text-center">
              <div className="h-12 border-b-2 border-navy-700 mb-2" />
              <p className="text-xs font-bold text-navy-700">Nakamya Grace</p>
              <p className="text-xs text-gray-500">Senior District Officer (Supervisor)</p>
              <p className="text-xs text-gray-500">Mbarara District Local Government</p>
            </div>
          </div>

          <div className="flex items-center justify-center">
            <div className="w-24 h-24 rounded-full border-4 border-navy-700 border-dashed flex items-center justify-center text-center">
              <div>
                <div className="text-xs font-bold text-navy-700 uppercase leading-tight">Official</div>
                <div className="text-xs font-bold text-navy-700 uppercase leading-tight">Stamp</div>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-xl p-4 text-center text-xs text-gray-500">
            <p className="font-mono font-bold text-gray-700 mb-1">{permitNumber}</p>
            <p>Verify authenticity at: nilegov.mbarara.go.ug/verify/{permitNumber}</p>
            <p className="mt-2 text-yellow-700 font-semibold">⚠ PROTOTYPE — This certificate is a demonstration only and has no legal force.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
