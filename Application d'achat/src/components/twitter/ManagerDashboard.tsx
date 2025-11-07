import React, { useState } from 'react';
import { ArrowLeft, TrendingUp, Clock, CheckCircle, Users, Award, Target, Star, Calendar, AlertTriangle } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Progress } from '../ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ManagerDashboardProps {
  onBack: () => void;
  onViewSettings: () => void;
  onSwitchRole: (role: string) => void;
}

// Mock data for unassigned tweets
interface UnassignedTweet {
  id: string;
  author: string;
  content: string;
  priority: 'low' | 'medium' | 'high';
  category: string;
  timestamp: Date;
}

const UNASSIGNED_TWEETS: UnassignedTweet[] = [
  {
    id: '1',
    author: 'Jean Dupont',
    content: '@Free Bonjour, je n\'ai plus internet depuis ce matin.',
    priority: 'high',
    category: 'Panne Internet',
    timestamp: new Date('2025-11-03T14:25:00')
  },
  {
    id: '4',
    author: 'Sophie Dubois',
    content: '@Free Impossible de me connecter à mon espace client.',
    priority: 'medium',
    category: 'Espace Client',
    timestamp: new Date('2025-11-03T13:45:00')
  },
  {
    id: '5',
    author: 'Luc Thomas',
    content: '@Free Quand est-ce que la fibre sera disponible dans ma zone ?',
    priority: 'low',
    category: 'Fibre',
    timestamp: new Date('2025-11-03T13:30:00')
  },
  {
    id: '7',
    author: 'Antoine Roux',
    content: '@Free Bonjour, comment puis-je résilier mon abonnement mobile ?',
    priority: 'medium',
    category: 'Résiliation',
    timestamp: new Date('2025-11-03T12:00:00')
  }
];

export default function ManagerDashboard({ onBack, onViewSettings, onSwitchRole }: ManagerDashboardProps) {
  const [dateFilter, setDateFilter] = useState<'week' | 'month'>('week');
  // Données de performance des agents
  const agentPerformance = [
    { 
      name: 'Agent 1', 
      traites: 45, 
      resolus: 38, 
      enCours: 7,
      tempsReponse: 12,
      satisfaction: 4.5,
      tauxResolution: 84
    },
    { 
      name: 'Agent 2', 
      traites: 52, 
      resolus: 47, 
      enCours: 5,
      tempsReponse: 8,
      satisfaction: 4.8,
      tauxResolution: 90
    },
    { 
      name: 'Agent 3', 
      traites: 38, 
      resolus: 30, 
      enCours: 8,
      tempsReponse: 15,
      satisfaction: 4.2,
      tauxResolution: 79
    },
    { 
      name: 'Agent 4', 
      traites: 41, 
      resolus: 35, 
      enCours: 6,
      tempsReponse: 10,
      satisfaction: 4.6,
      tauxResolution: 85
    },
    { 
      name: 'Agent 5', 
      traites: 49, 
      resolus: 44, 
      enCours: 5,
      tempsReponse: 9,
      satisfaction: 4.7,
      tauxResolution: 90
    }
  ];

  // Catégories de tickets
  const categoryData = [
    { name: 'Panne Internet', value: 145, percentage: 28 },
    { name: 'Facturation', value: 98, percentage: 19 },
    { name: 'Débit Internet', value: 87, percentage: 17 },
    { name: 'Espace Client', value: 76, percentage: 15 },
    { name: 'Fibre', value: 54, percentage: 10 },
    { name: 'Résiliation', value: 32, percentage: 6 },
    { name: 'Remerciement', value: 25, percentage: 5 }
  ];

  const CATEGORY_COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4'];

  // Temps de réponse moyen par jour (sans dimanche)
  const responseTimeData = [
    { jour: 'Lun', temps: 12 },
    { jour: 'Mar', temps: 10 },
    { jour: 'Mer', temps: 14 },
    { jour: 'Jeu', temps: 11 },
    { jour: 'Ven', temps: 9 },
    { jour: 'Sam', temps: 15 }
  ];

  // Tweets traités par jour (sans dimanche)
  const tweetsPerDayData = [
    { jour: 'Lun', tweets: 42, resolus: 38 },
    { jour: 'Mar', tweets: 55, resolus: 50 },
    { jour: 'Mer', tweets: 48, resolus: 41 },
    { jour: 'Jeu', tweets: 61, resolus: 56 },
    { jour: 'Ven', tweets: 52, resolus: 48 },
    { jour: 'Sam', tweets: 35, resolus: 30 }
  ];

  // Statistiques globales
  const totalTweets = 225;
  const avgPerDay = 32;
  const avgResponseTime = 11;
  const resolutionRate = 86;
  const satisfactionScore = 4.6;

  return (
    <div className="flex flex-col h-full bg-gray-50 overflow-auto">
      {/* Header */}
      <div className="bg-white border-b p-6 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-[#e20e18]">Tableau de Bord Manager</h1>
            <p className="text-gray-600">Vue performance équipe</p>
          </div>
          <div className="flex gap-2">
            <Select value={dateFilter} onValueChange={(v) => setDateFilter(v as any)}>
              <SelectTrigger className="w-[150px]">
                <Calendar className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="week">Cette semaine</SelectItem>
                <SelectItem value="month">Ce mois</SelectItem>
              </SelectContent>
            </Select>
            <Select defaultValue="manager" onValueChange={onSwitchRole}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="agent">👤 Vue Agent</SelectItem>
                <SelectItem value="manager">👔 Vue Manager</SelectItem>
                <SelectItem value="director">📊 Vue Directeur</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={onViewSettings}>
              Paramètres
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* KPIs globaux */}
        <div className="grid grid-cols-5 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Tweets/jour</p>
                <p className="text-blue-600">{avgPerDay}</p>
              </div>
              <Target className="w-8 h-8 text-blue-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Taux résolution</p>
                <p className="text-green-600">{resolutionRate}%</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Temps réponse</p>
                <p className="text-orange-600">{avgResponseTime}min</p>
              </div>
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Satisfaction</p>
                <p className="text-purple-600">{satisfactionScore}/5</p>
              </div>
              <Star className="w-8 h-8 text-purple-600 fill-purple-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Agents actifs</p>
                <p className="text-indigo-600">{agentPerformance.length}</p>
              </div>
              <Users className="w-8 h-8 text-indigo-600" />
            </div>
          </Card>
        </div>

        {/* Tweets non assignés */}
        <Card className="p-6 border-l-4 border-l-purple-500">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-purple-600" />
            <h3 className="text-gray-700">Tweets non assignés - À assigner aux agents</h3>
            <Badge className="bg-purple-100 text-purple-800">{UNASSIGNED_TWEETS.length}</Badge>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Auteur</TableHead>
                <TableHead>Contenu</TableHead>
                <TableHead>Priorité</TableHead>
                <TableHead>Catégorie</TableHead>
                <TableHead>Temps d'attente</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {UNASSIGNED_TWEETS.map(tweet => {
                const minutes = Math.floor((Date.now() - tweet.timestamp.getTime()) / 1000 / 60);
                return (
                  <TableRow key={tweet.id}>
                    <TableCell>{tweet.author}</TableCell>
                    <TableCell className="max-w-md truncate">{tweet.content}</TableCell>
                    <TableCell>
                      <Badge className={
                        tweet.priority === 'high' ? 'bg-red-100 text-red-800' :
                        tweet.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }>
                        {tweet.priority === 'high' ? 'Haute' : tweet.priority === 'medium' ? 'Moyenne' : 'Basse'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{tweet.category}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={minutes > 60 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}>
                        {minutes}m
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Select>
                        <SelectTrigger className="w-[120px]">
                          <SelectValue placeholder="Assigner à" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="agent1">Agent 1</SelectItem>
                          <SelectItem value="agent2">Agent 2</SelectItem>
                          <SelectItem value="agent3">Agent 3</SelectItem>
                          <SelectItem value="agent4">Agent 4</SelectItem>
                          <SelectItem value="agent5">Agent 5</SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>

        {/* Performance des agents */}
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-5 h-5 text-blue-600" />
            <h3 className="text-gray-700">Performance par agent</h3>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Agent</TableHead>
                <TableHead>Tweets traités</TableHead>
                <TableHead>Résolus</TableHead>
                <TableHead>Taux résolution</TableHead>
                <TableHead>Temps réponse</TableHead>
                <TableHead>Satisfaction</TableHead>
                <TableHead>Performance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {agentPerformance.map((agent, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xs">
                        {agent.name.slice(-1)}
                      </div>
                      <span>{agent.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{agent.traites}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className="bg-green-100 text-green-800">{agent.resolus}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress value={agent.tauxResolution} className="w-20 h-2" />
                      <span className="text-xs">{agent.tauxResolution}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={
                      agent.tempsReponse <= 10 ? 'bg-green-100 text-green-800' :
                      agent.tempsReponse <= 15 ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }>
                      {agent.tempsReponse}min
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                      <span>{agent.satisfaction}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    {agent.tauxResolution >= 85 && agent.satisfaction >= 4.5 ? (
                      <Badge className="bg-green-100 text-green-800">Excellent</Badge>
                    ) : agent.tauxResolution >= 80 ? (
                      <Badge className="bg-blue-100 text-blue-800">Bon</Badge>
                    ) : (
                      <Badge className="bg-orange-100 text-orange-800">À améliorer</Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>

        {/* Charts row 1 */}
        <div className="grid grid-cols-2 gap-6">
          {/* Temps de réponse */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-5 h-5 text-orange-600" />
              <h3 className="text-gray-700">Temps de réponse moyen (minutes)</h3>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="jour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="temps" stroke="#f59e0b" strokeWidth={2} name="Temps (min)" />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Tweets traités */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h3 className="text-gray-700">Tweets traités par jour</h3>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={tweetsPerDayData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="jour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="tweets" fill="#3b82f6" name="Reçus" />
                <Bar dataKey="resolus" fill="#10b981" name="Résolus" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Catégories de tickets */}
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-purple-600" />
            <h3 className="text-gray-700">Catégories de tickets</h3>
          </div>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ percentage }) => `${percentage}%`}
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              {categoryData.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: CATEGORY_COLORS[index] }}
                    />
                    <span className="text-xs">{category.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-600">{category.value}</span>
                    <Badge variant="outline" className="text-xs">{category.percentage}%</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>


      </div>
    </div>
  );
}
