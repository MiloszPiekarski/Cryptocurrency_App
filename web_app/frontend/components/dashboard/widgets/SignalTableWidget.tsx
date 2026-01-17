import React, { useMemo } from 'react';
import {
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
    flexRender,
    createColumnHelper,
    SortingState,
} from '@tanstack/react-table';
import { Search, ChevronDown, ChevronUp, ExternalLink, WifiOff } from 'lucide-react';

interface SignalTableWidgetProps {
    data: any[] | null | undefined;
    onDeepDive: (agentData: any) => void;
    loading?: boolean;
}

const columnHelper = createColumnHelper<any>();

export const SignalTableWidget: React.FC<SignalTableWidgetProps> = ({ data, onDeepDive, loading }) => {
    const [sorting, setSorting] = React.useState<SortingState>([]);

    const columns = useMemo(() => [
        columnHelper.accessor('role', {
            header: 'AGENT ROLE',
            cell: info => <div className="font-bold text-xs text-slate-200">{info.getValue()}</div>
        }),
        columnHelper.accessor('signal', {
            header: 'SIGNAL',
            cell: info => {
                const val = info.getValue();
                const color = val === 'BUY' ? 'text-emerald-400 bg-emerald-400/10' :
                    val === 'SELL' ? 'text-rose-400 bg-rose-400/10' :
                        'text-amber-400 bg-amber-400/10';
                return (
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${color}`}>
                        {val}
                    </span>
                );
            }
        }),
        columnHelper.accessor('confidence', {
            header: 'CONF %',
            cell: info => <div className="text-slate-400 font-mono">{info.getValue()}%</div>
        }),
        columnHelper.accessor('reasoning', {
            header: 'AI REASONING',
            cell: info => (
                <div className="flex flex-col gap-2 min-w-[300px] max-w-[600px]">
                    <p className="text-[11px] text-slate-300 whitespace-normal break-words leading-relaxed font-mono">
                        {info.getValue()}
                    </p>

                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onDeepDive(info.row.original);
                        }}
                        className="text-[10px] text-blue-400 hover:text-blue-300 self-start mt-1 font-mono uppercase tracking-wider flex items-center gap-1"
                    >
                        [ View Neural Logic ]
                    </button>
                </div>
            )
        }),
        columnHelper.display({
            id: 'actions',
            header: 'PROOF',
            cell: props => (
                <button
                    onClick={() => onDeepDive(props.row.original)}
                    className="flex items-center gap-1.5 px-2 py-1 bg-blue-500/10 hover:bg-blue-500/20 rounded text-[10px] font-bold text-blue-400 transition-colors uppercase tracking-tight"
                >
                    <ExternalLink size={10} />
                    DEEP DIVE
                </button>
            )
        })
    ], [onDeepDive]);

    // Data comes from: GET /api/v1/hive/swarm/BTC/USDT → response.swarm_breakdown
    // This is an array of agent results, each containing: role, signal, confidence, reasoning
    const agentData = data || [];

    const table = useReactTable({
        data: agentData,
        columns,
        state: { sorting },
        onSortingChange: setSorting,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
    });

    return (
        <div className="h-auto flex flex-col bg-slate-900/50 rounded-xl border border-slate-700/50">
            <div className="p-3 border-b border-slate-800 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Search size={14} className="text-slate-500" />
                    <span className="text-xs font-bold text-slate-400 font-mono tracking-wider">EVIDENCE LOG</span>
                </div>
                <div className="text-[10px] text-slate-600 font-mono">
                    {agentData.length} SIGNALS
                </div>
            </div>

            {/* LOADING STATE */}
            {loading && (
                <div className="h-64 flex items-center justify-center">
                    <div className="text-slate-500 text-xs font-mono animate-pulse">LOADING AGENT DATA...</div>
                </div>
            )}

            {/* OFFLINE STATE - No data and not loading */}
            {!loading && agentData.length === 0 && (
                <div className="h-64 flex flex-col items-center justify-center">
                    <WifiOff size={24} className="text-rose-500 mb-2" />
                    <div className="text-rose-400 text-xs font-mono font-bold">NO SIGNALS</div>
                    <div className="text-slate-500 text-[10px] font-mono mt-1">Waiting for agent data from backend</div>
                </div>
            )}

            {/* DATA TABLE - Only shown when we have REAL data */}
            {!loading && agentData.length > 0 && (
                <div className="w-full">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-slate-900/80 sticky top-0 z-10 backdrop-blur-sm">
                            {table.getHeaderGroups().map(headerGroup => (
                                <tr key={headerGroup.id}>
                                    {headerGroup.headers.map(header => (
                                        <th key={header.id} className="p-3 text-[10px] font-bold text-slate-500 border-b border-slate-800 select-none cursor-pointer hover:text-slate-300 transition-colors" onClick={header.column.getToggleSortingHandler()}>
                                            <div className="flex items-center gap-1">
                                                {flexRender(header.column.columnDef.header, header.getContext())}
                                                {{
                                                    asc: <ChevronUp size={10} />,
                                                    desc: <ChevronDown size={10} />,
                                                }[header.column.getIsSorted() as string] ?? null}
                                            </div>
                                        </th>
                                    ))}
                                </tr>
                            ))}
                        </thead>
                        <tbody>
                            {table.getRowModel().rows.map(row => (
                                <tr key={row.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                                    {row.getVisibleCells().map(cell => (
                                        <td key={cell.id} className="p-3">
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
