import React, { useState } from "react";
import {
  TrendingUp,
  Activity,
  Clock,
  ThumbsUp,
  BarChart3,
  PieChart as PieChartIcon,
  TrendingDown,
  Calendar,
} from "lucide-react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Progress } from "../ui/progress";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface DirectorDashboardProps {
  onBack: () => void;
  onViewSettings: () => void;
  onSwitchRole: (role: string) => void;
}

export default function DirectorDashboard({
  onBack,
  onViewSettings,
  onSwitchRole,
}: DirectorDashboardProps) {
  const [dateFilter, setDateFilter] = useState<
    "week" | "month"
  >("month");
  // Volume de requêtes par mois
  const volumeData = [
    { mois: "Jan", volume: 1245, traites: 1198, resolus: 1087 },
    { mois: "Fév", volume: 1389, traites: 1345, resolus: 1234 },
    { mois: "Mar", volume: 1567, traites: 1523, resolus: 1401 },
    { mois: "Avr", volume: 1423, traites: 1398, resolus: 1289 },
    { mois: "Mai", volume: 1678, traites: 1654, resolus: 1523 },
    { mois: "Jun", volume: 1834, traites: 1812, resolus: 1678 },
    { mois: "Jul", volume: 1956, traites: 1923, resolus: 1789 },
  ];

  // Sentiments
  const sentimentData = [
    { name: "Positif", value: 342, percentage: 28 },
    { name: "Neutre", value: 598, percentage: 49 },
    { name: "Négatif", value: 281, percentage: 23 },
  ];

  const SENTIMENT_COLORS = ["#10b981", "#6b7280", "#ef4444"];

  // Taux de traitement par semaine
  const traitementData = [
    { semaine: "S1", taux: 92, temps: 13 },
    { semaine: "S2", taux: 94, temps: 11 },
    { semaine: "S3", taux: 91, temps: 14 },
    { semaine: "S4", taux: 96, temps: 10 },
    { semaine: "S5", taux: 93, temps: 12 },
    { semaine: "S6", taux: 95, temps: 9 },
    { semaine: "S7", taux: 97, temps: 8 },
  ];

  // Satisfaction client par mois
  const satisfactionData = [
    { mois: "Jan", score: 4.2 },
    { mois: "Fév", score: 4.3 },
    { mois: "Mar", score: 4.5 },
    { mois: "Avr", score: 4.4 },
    { mois: "Mai", score: 4.6 },
    { mois: "Jun", score: 4.7 },
    { mois: "Jul", score: 4.8 },
  ];

  // KPIs principaux
  const totalVolume = 1956;
  const tauxTraitement = 98.3;
  const tempsTraitementMoyen = 8.5;
  const satisfactionGlobale = 4.8;
  const evolutionVolume = 12.4; // % vs mois précédent
  const evolutionSatisfaction = 2.1; // % vs mois précédent

  return (
    <div className="flex flex-col h-full bg-gray-50 overflow-auto">
      {/* Header */}
      <div className="bg-white border-b p-6 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-[#e20e18]">
              Tableau de Bord Direction
            </h1>
            <p className="text-gray-600">
              Vue stratégique et KPIs
            </p>
          </div>
          <div className="flex gap-2">
            <Select
              value={dateFilter}
              onValueChange={(v) => setDateFilter(v as any)}
            >
              <SelectTrigger className="w-[150px]">
                <Calendar className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="week">
                  Cette semaine
                </SelectItem>
                <SelectItem value="month">Ce mois</SelectItem>
              </SelectContent>
            </Select>
            <Select
              defaultValue="director"
              onValueChange={onSwitchRole}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="agent">
                  👤 Vue Agent
                </SelectItem>
                <SelectItem value="manager">
                  👔 Vue Manager
                </SelectItem>
                <SelectItem value="director">
                  📊 Vue Directeur
                </SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={onViewSettings}>
              Paramètres
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* KPIs principaux */}
        <div className="grid grid-cols-4 gap-4">
          <Card className="p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-blue-100 text-xs mb-1">
                  Volume de requêtes
                </p>
                <p className="text-3xl mb-1">
                  {totalVolume.toLocaleString()}
                </p>
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs">
                    +{evolutionVolume}% vs mois dernier
                  </span>
                </div>
              </div>
              <Activity className="w-10 h-10 opacity-80" />
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-green-100 text-xs mb-1">
                  Taux de traitement
                </p>
                <p className="text-3xl mb-1">
                  {tauxTraitement}%
                </p>
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs">Excellent</span>
                </div>
              </div>
              <BarChart3 className="w-10 h-10 opacity-80" />
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-orange-500 to-orange-600 text-white">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-orange-100 text-xs mb-1">
                  Temps de traitement
                </p>
                <p className="text-3xl mb-1">
                  {tempsTraitementMoyen} min
                </p>
                <div className="flex items-center gap-1">
                  <TrendingDown className="w-4 h-4" />
                  <span className="text-xs">-15% ce mois</span>
                </div>
              </div>
              <Clock className="w-10 h-10 opacity-80" />
            </div>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-purple-100 text-xs mb-1">
                  Satisfaction client
                </p>
                <p className="text-3xl mb-1">
                  {satisfactionGlobale}/5
                </p>
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs">
                    +{evolutionSatisfaction}% vs mois dernier
                  </span>
                </div>
              </div>
              <ThumbsUp className="w-10 h-10 opacity-80" />
            </div>
          </Card>
        </div>

        {/* Volume de requêtes */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <h3 className="text-gray-700">
                Volume de requêtes et traitement
              </h3>
            </div>
            <Select defaultValue="7mois">
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7mois">
                  7 derniers mois
                </SelectItem>
                <SelectItem value="3mois">
                  3 derniers mois
                </SelectItem>
                <SelectItem value="12mois">
                  12 derniers mois
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={volumeData}>
              <defs>
                <linearGradient
                  id="colorVolume"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="5%"
                    stopColor="#3b82f6"
                    stopOpacity={0.8}
                  />
                  <stop
                    offset="95%"
                    stopColor="#3b82f6"
                    stopOpacity={0}
                  />
                </linearGradient>
                <linearGradient
                  id="colorResolus"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="5%"
                    stopColor="#10b981"
                    stopOpacity={0.8}
                  />
                  <stop
                    offset="95%"
                    stopColor="#10b981"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mois" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="volume"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorVolume)"
                name="Volume reçu"
              />
              <Area
                type="monotone"
                dataKey="resolus"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorResolus)"
                name="Résolus"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Row 2 */}
        <div className="grid grid-cols-2 gap-6">
          {/* Taux de traitement */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-green-600" />
              <h3 className="text-gray-700">
                Taux de traitement et temps moyen
              </h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={traitementData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="semaine" />
                <YAxis
                  yAxisId="left"
                  orientation="left"
                  stroke="#10b981"
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  stroke="#f59e0b"
                />
                <Tooltip />
                <Legend />
                <Bar
                  yAxisId="left"
                  dataKey="taux"
                  fill="#10b981"
                  name="Taux traitement (%)"
                />
                <Bar
                  yAxisId="right"
                  dataKey="temps"
                  fill="#f59e0b"
                  name="Temps moyen (min)"
                />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Satisfaction */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <ThumbsUp className="w-5 h-5 text-purple-600" />
              <h3 className="text-gray-700">
                Évolution de la satisfaction client
              </h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={satisfactionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mois" />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#8b5cf6"
                  strokeWidth={3}
                  name="Score satisfaction"
                  dot={{ fill: "#8b5cf6", r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Sentiments */}
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <PieChartIcon className="w-5 h-5 text-indigo-600" />
            <h3 className="text-gray-700">
              Répartition des sentiments
            </h3>
          </div>
          <div className="flex items-center gap-8">
            <ResponsiveContainer width="50%" height={250}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ percentage }) => `${percentage}%`}
                  outerRadius={90}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={SENTIMENT_COLORS[index]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-4">
              {sentimentData.map((sentiment, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-4 h-4 rounded-full"
                        style={{
                          backgroundColor:
                            SENTIMENT_COLORS[index],
                        }}
                      />
                      <span>{sentiment.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">
                        {sentiment.value}
                      </span>
                      <Badge variant="outline">
                        {sentiment.percentage}%
                      </Badge>
                    </div>
                  </div>
                  <Progress
                    value={sentiment.percentage}
                    className="h-2"
                  />
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Insights stratégiques */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="p-6 border-l-4 border-l-blue-500">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-gray-600 text-xs">
                  Croissance
                </p>
                <p className="text-blue-600">+12.4%</p>
              </div>
            </div>
            <p className="text-gray-600 text-xs">
              Le volume de requêtes continue d'augmenter.
              Envisager le recrutement de 2 agents
              supplémentaires.
            </p>
          </Card>

          <Card className="p-6 border-l-4 border-l-green-500">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <ThumbsUp className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-gray-600 text-xs">
                  Performance
                </p>
                <p className="text-green-600">Excellente</p>
              </div>
            </div>
            <p className="text-gray-600 text-xs">
              Taux de traitement de 98.3% et satisfaction en
              hausse. Objectifs trimestriels dépassés.
            </p>
          </Card>

          <Card className="p-6 border-l-4 border-l-orange-500">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                <Clock className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-gray-600 text-xs">
                  Optimisation
                </p>
                <p className="text-orange-600">-15%</p>
              </div>
            </div>
            <p className="text-gray-600 text-xs">
              Temps de traitement réduit grâce à l'IA. Continuer
              l'automatisation des réponses simples.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}