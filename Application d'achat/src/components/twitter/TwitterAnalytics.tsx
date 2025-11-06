import React from "react";
import { ArrowLeft, TrendingUp, MessageSquare, Clock, Heart } from "lucide-react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface TwitterAnalyticsProps {
  onBack: () => void;
}

export default function TwitterAnalytics({ onBack }: TwitterAnalyticsProps) {
  // Mock data
  const weeklyData = [
    { jour: 'Lun', tweets: 45, resolus: 42 },
    { jour: 'Mar', tweets: 52, resolus: 48 },
    { jour: 'Mer', tweets: 38, resolus: 36 },
    { jour: 'Jeu', tweets: 61, resolus: 58 },
    { jour: 'Ven', tweets: 49, resolus: 46 },
    { jour: 'Sam', tweets: 28, resolus: 27 },
  ];

  const categoryData = [
    { name: 'Panne Internet', value: 35 },
    { name: 'Facturation', value: 28 },
    { name: 'Espace Client', value: 18 },
    { name: 'Fibre', value: 12 },
    { name: 'Autres', value: 7 },
  ];

  const COLORS = ['#e20e18', '#f59e0b', '#3b82f6', '#10b981', '#6b7280'];

  const responseTimeData = [
    { heure: '09:00', temps: 5.2 },
    { heure: '10:00', temps: 4.8 },
    { heure: '11:00', temps: 6.1 },
    { heure: '12:00', temps: 7.5 },
    { heure: '14:00', temps: 5.9 },
    { heure: '15:00', temps: 4.3 },
    { heure: '16:00', temps: 5.7 },
    { heure: '17:00', temps: 6.8 },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b p-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-[#e20e18]">Analytiques</h1>
            <p className="text-gray-600">Vue d'ensemble de votre performance</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* KPIs */}
        <div className="grid grid-cols-4 gap-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              <h3 className="text-gray-600">Tweets traités</h3>
            </div>
            <p className="text-gray-900">273</p>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-green-600 text-sm">+12%</span>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-orange-600" />
              <h3 className="text-gray-600">Temps moyen</h3>
            </div>
            <p className="text-gray-900">5.8 min</p>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-green-600 text-sm">-8%</span>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <Heart className="w-5 h-5 text-red-600" />
              <h3 className="text-gray-600">Satisfaction</h3>
            </div>
            <p className="text-gray-900">4.7/5</p>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-green-600 text-sm">+5%</span>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="text-gray-600">Taux résolution</h3>
            </div>
            <p className="text-gray-900">94.5%</p>
            <Progress value={94.5} className="mt-2" />
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          {/* Weekly Activity */}
          <Card className="p-6">
            <h3 className="text-gray-700 mb-4">Activité hebdomadaire</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="jour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="tweets" fill="#e20e18" name="Reçus" />
                <Bar dataKey="resolus" fill="#10b981" name="Résolus" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Category Distribution */}
          <Card className="p-6">
            <h3 className="text-gray-700 mb-4">Distribution par catégorie</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>

          {/* Response Time Trend */}
          <Card className="p-6 col-span-2">
            <h3 className="text-gray-700 mb-4">Évolution du temps de réponse</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="heure" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="temps"
                  stroke="#e20e18"
                  strokeWidth={2}
                  name="Temps (min)"
                  dot={{ fill: '#e20e18', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Performance Summary */}
        <Card className="p-6">
          <h3 className="text-gray-700 mb-4">Résumé de performance</h3>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-gray-600 mb-2">Tweets en attente</p>
              <p className="text-gray-900">12</p>
              <Progress value={15} className="mt-2" />
            </div>
            <div>
              <p className="text-gray-600 mb-2">En cours de traitement</p>
              <p className="text-gray-900">8</p>
              <Progress value={10} className="mt-2" />
            </div>
            <div>
              <p className="text-gray-600 mb-2">Résolus aujourd'hui</p>
              <p className="text-gray-900">45</p>
              <Progress value={75} className="mt-2" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
