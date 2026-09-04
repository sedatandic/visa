import React from "react";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { BarChart3 } from "lucide-react";
import { formatMoney } from "../lib/site";

const INSURANCE_COLOR = "hsl(30 62% 42%)";
const ESIM_COLOR = "hsl(38 82% 58%)";

export const MonthlyProfitChart = ({ data }) => {
    if (!data) return null;
    const { items, totals } = data;

    return (
        <div className="card-surface p-5 sm:p-6" data-testid="monthly-profit-chart">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="flex items-center gap-2 font-heading text-sm font-bold">
                    <BarChart3 className="h-4 w-4 text-primary" /> Aylık kâr özeti (son 12 ay)
                </h2>
                <div className="flex flex-wrap gap-5 text-xs">
                    <span data-testid="monthly-total-insurance">
                        Sigorta kârı:{" "}
                        <b className="text-foreground">
                            {formatMoney(totals.insurance_profit, "TRY")}
                        </b>
                    </span>
                    <span data-testid="monthly-total-esim">
                        eSIM kârı:{" "}
                        <b className="text-foreground">{formatMoney(totals.esim_profit, "TRY")}</b>
                    </span>
                    <span data-testid="monthly-total-profit">
                        Toplam:{" "}
                        <b className="text-emerald-700">
                            {formatMoney(totals.total_profit, "TRY")}
                        </b>
                    </span>
                </div>
            </div>

            <div className="mt-6 h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={items} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 90%)" vertical={false} />
                        <XAxis dataKey="label" tick={{ fontSize: 12 }} tickLine={false} />
                        <YAxis
                            tick={{ fontSize: 12 }}
                            tickLine={false}
                            axisLine={false}
                            width={70}
                            tickFormatter={(v) => `${Math.round(v).toLocaleString("tr-TR")} ₺`}
                        />
                        <Tooltip
                            formatter={(value, name) => [formatMoney(value, "TRY"), name]}
                            labelFormatter={(label) => `Ay: ${label}`}
                        />
                        <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                        <Bar
                            dataKey="insurance_profit"
                            name="Sigorta kârı"
                            stackId="p"
                            fill={INSURANCE_COLOR}
                            radius={[0, 0, 0, 0]}
                        />
                        <Bar
                            dataKey="esim_profit"
                            name="eSIM kârı"
                            stackId="p"
                            fill={ESIM_COLOR}
                            radius={[6, 6, 0, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
