import React, { useState } from 'react';
import { MessageCircle, AlertCircle, CheckCircle, Clock, Search, Filter, TrendingUp, AlertTriangle, Award, Target, Calendar } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Progress } from '../ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';

interface Tweet {
  id: string;
  author: string;
  handle: string;
  content: string;
  timestamp: Date;
  status: 'pending' | 'in-progress' | 'resolved';
  priority: 'low' | 'medium' | 'high';
  category: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  confidence?: number;
  assignedTo?: string;
}

interface AgentDashboardProps {
  onTweetSelect: (tweet: Tweet) => void;
  onViewAnalytics: () => void;
  onViewSettings: () => void;
  onSwitchRole: (role: string) => void;
}

const MOCK_TWEETS: Tweet[] = [
  {
    id: '1',
    author: 'Jean Dupont',
    handle: '@jeandupont',
    content: '@Free Bonjour, je n\'ai plus internet depuis ce matin. Pouvez-vous m\'aider ? C\'est urgent pour mon travail.',
    timestamp: new Date('2025-11-03T14:25:00'),
    status: 'pending',
    priority: 'high',
    category: 'Panne Internet',
    sentiment: 'negative',
    confidence: 85
  },
  {
    id: '2',
    author: 'Marie Martin',
    handle: '@mariemartin',
    content: '@Free Merci pour votre excellent service client ! Problème résolu en 10 minutes 👍',
    timestamp: new Date('2025-11-03T14:15:00'),
    status: 'resolved',
    priority: 'low',
    category: 'Remerciement',
    sentiment: 'positive',
    confidence: 95,
    assignedTo: 'Agent 1'
  },
  {
    id: '3',
    author: 'Pierre Bernard',
    handle: '@pierrebernard',
    content: '@Free Ma facture de ce mois semble incorrecte. Comment puis-je la contester ?',
    timestamp: new Date('2025-11-03T14:00:00'),
    status: 'in-progress',
    priority: 'medium',
    category: 'Facturation',
    sentiment: 'neutral',
    confidence: 78,
    assignedTo: 'Agent 1'
  },
  {
    id: '4',
    author: 'Sophie Dubois',
    handle: '@sophiedubois',
    content: '@Free Impossible de me connecter à mon espace client. Le mot de passe ne fonctionne pas.',
    timestamp: new Date('2025-11-03T13:45:00'),
    status: 'pending',
    priority: 'medium',
    category: 'Espace Client',
    sentiment: 'negative',
    confidence: 82
  },
  {
    id: '5',
    author: 'Luc Thomas',
    handle: '@lucthomas',
    content: '@Free Quand est-ce que la fibre sera disponible dans ma zone ? (75018)',
    timestamp: new Date('2025-11-03T13:30:00'),
    status: 'pending',
    priority: 'low',
    category: 'Fibre',
    sentiment: 'neutral',
    confidence: 88
  },
  {
    id: '6',
    author: 'Camille Petit',
    handle: '@camillepetit',
    content: '@Free Débit internet très lent depuis hier soir. Speed test : 2 Mb/s au lieu de 100 Mb/s.',
    timestamp: new Date('2025-11-03T13:00:00'),
    status: 'in-progress',
    priority: 'high',
    category: 'Débit Internet',
    sentiment: 'negative',
    confidence: 92,
    assignedTo: 'Agent 1'
  },
  {
    id: '7',
    author: 'Antoine Roux',
    handle: '@antoineroux',
    content: '@Free Bonjour, comment puis-je résilier mon abonnement mobile ?',
    timestamp: new Date('2025-11-03T12:00:00'),
    status: 'pending',
    priority: 'medium',
    category: 'Résiliation',
    sentiment: 'neutral',
    confidence: 75
  },
  {
    id: '8',
    author: 'Emma Leroy',
    handle: '@emmaleroy',
    content: '@Free La nouvelle Freebox Ultra est incroyable ! Installation parfaite 🎉',
    timestamp: new Date('2025-11-03T11:30:00'),
    status: 'resolved',
    priority: 'low',
    category: 'Remerciement',
    sentiment: 'positive',
    confidence: 98,
    assignedTo: 'Agent 2'
  }
];

export default function AgentDashboard({ onTweetSelect, onViewAnalytics, onViewSettings, onSwitchRole }: AgentDashboardProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'unassigned' | 'in-progress' | 'assigned'>('all');
  const [urgencyFilter, setUrgencyFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [dateFilter, setDateFilter] = useState<'all' | 'today' | 'week' | 'month'>('all');
  const [tweets] = useState<Tweet[]>(MOCK_TWEETS);

  const filteredTweets = tweets.filter(tweet => {
    const matchesSearch = tweet.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tweet.author.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter
    let matchesStatus = true;
    if (statusFilter === 'unassigned') {
      matchesStatus = !tweet.assignedTo && tweet.status !== 'resolved';
    } else if (statusFilter === 'in-progress') {
      matchesStatus = tweet.status === 'in-progress';
    } else if (statusFilter === 'assigned') {
      matchesStatus = tweet.assignedTo !== undefined && tweet.status !== 'resolved';
    }
    
    const matchesUrgency = urgencyFilter === 'all' || tweet.priority === urgencyFilter;
    
    // Date filter
    let matchesDate = true;
    if (dateFilter !== 'all') {
      const now = new Date();
      const tweetDate = tweet.timestamp;
      
      if (dateFilter === 'today') {
        matchesDate = tweetDate.toDateString() === now.toDateString();
      } else if (dateFilter === 'week') {
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        matchesDate = tweetDate >= weekAgo;
      } else if (dateFilter === 'month') {
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        matchesDate = tweetDate >= monthAgo;
      }
    }
    
    return matchesSearch && matchesStatus && matchesUrgency && matchesDate && tweet.status !== 'resolved';
  });

  // Tweets avec confiance < 90%
  const lowConfidenceTweets = tweets.filter(t => (t.confidence || 0) < 90 && t.status !== 'resolved');
  
  // Tweets urgents
  const urgentTweets = tweets.filter(t => t.priority === 'high' && t.status !== 'resolved');
  
  // Tweets non assignés (restants)
  const unassignedTweets = tweets.filter(t => !t.assignedTo && t.status !== 'resolved');
  
  // Performance personnelle (Agent 1)
  const myTweets = tweets.filter(t => t.assignedTo === 'Agent 1' && t.status !== 'resolved');
  const myInProgress = myTweets.filter(t => t.status === 'in-progress').length;
  const myAssigned = myTweets.length;
  
  const assignedCount = tweets.filter(t => t.assignedTo && t.status !== 'resolved').length;
  const inProgressCount = tweets.filter(t => t.status === 'in-progress').length;
  
  const highUrgencyCount = tweets.filter(t => t.priority === 'high' && t.status !== 'resolved').length;

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-[#e20e18]">Tableau de Bord Agent</h1>
            <p className="text-gray-600">Vue opérationnelle</p>
          </div>
          <div className="flex gap-2">
            <Select defaultValue="agent" onValueChange={onSwitchRole}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="agent">👤 Vue Agent</SelectItem>
                <SelectItem value="manager">👔 Vue Manager</SelectItem>
                <SelectItem value="director">📊 Vue Directeur</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={onViewAnalytics}>
              <TrendingUp className="w-4 h-4 mr-2" />
              Analytiques
            </Button>
            <Button variant="outline" onClick={onViewSettings}>
              Paramètres
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Confiance {'<'} 90%</p>
                <p className="text-orange-600">{lowConfidenceTweets.length}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-orange-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Restants</p>
                <p className="text-purple-600">{unassignedTweets.length}</p>
              </div>
              <Clock className="w-8 h-8 text-purple-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">Assignés</p>
                <p className="text-blue-600">{assignedCount}</p>
              </div>
              <Target className="w-8 h-8 text-blue-600" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600">En cours</p>
                <p className="text-green-600">{inProgressCount}</p>
              </div>
              <Award className="w-8 h-8 text-green-600" />
            </div>
          </Card>
        </div>

        {/* Performance personnelle */}
        <Card className="p-4 mb-4 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-blue-600" />
              <h3 className="text-gray-700">Ma performance aujourd'hui</h3>
            </div>
            <Badge className="bg-blue-100 text-blue-800">Agent 1</Badge>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600 text-xs">Mes tickets assignés</p>
              <p className="text-blue-600">{myAssigned}</p>
            </div>
            <div>
              <p className="text-gray-600 text-xs">En cours de traitement</p>
              <p className="text-orange-600">{myInProgress}</p>
            </div>
          </div>
        </Card>

        {/* Search and Filter */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Rechercher un tweet ou un auteur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={dateFilter} onValueChange={(v) => setDateFilter(v as any)}>
            <SelectTrigger className="w-[180px]">
              <Calendar className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Période" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toute période</SelectItem>
              <SelectItem value="today">Aujourd'hui</SelectItem>
              <SelectItem value="week">Cette semaine</SelectItem>
              <SelectItem value="month">Ce mois</SelectItem>
            </SelectContent>
          </Select>
          <Select value={urgencyFilter} onValueChange={(v) => setUrgencyFilter(v as any)}>
            <SelectTrigger className="w-[180px]">
              <AlertTriangle className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Urgence" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes urgences</SelectItem>
              <SelectItem value="high">Urgence haute</SelectItem>
              <SelectItem value="medium">Urgence moyenne</SelectItem>
              <SelectItem value="low">Urgence basse</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Priority Tables */}
      <div className="p-6 overflow-auto">
        <div className="space-y-4 mb-6">
          {/* Tweets avec faible confiance */}
          {lowConfidenceTweets.length > 0 && (
            <Card className="p-4 border-orange-200">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                <h3 className="text-gray-700">Tweets nécessitant une révision (Confiance {'<'} 90%)</h3>
                <Badge className="bg-orange-100 text-orange-800">{lowConfidenceTweets.length}</Badge>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Auteur</TableHead>
                    <TableHead>Contenu</TableHead>
                    <TableHead>Confiance</TableHead>
                    <TableHead>Catégorie</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lowConfidenceTweets.slice(0, 3).map(tweet => (
                    <TableRow key={tweet.id} className="cursor-pointer hover:bg-gray-50" onClick={() => onTweetSelect(tweet)}>
                      <TableCell>{tweet.author}</TableCell>
                      <TableCell className="max-w-md truncate">{tweet.content}</TableCell>
                      <TableCell>
                        <Badge className="bg-orange-100 text-orange-800">{tweet.confidence}%</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{tweet.category}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">Réviser</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}

          {/* Tweets non assignés (Restants) */}
          {unassignedTweets.length > 0 && (
            <Card className="p-4 border-purple-200">
              <div className="flex items-center gap-2 mb-3">
                <Clock className="w-5 h-5 text-purple-600" />
                <h3 className="text-gray-700">Tickets restants (non assignés)</h3>
                <Badge className="bg-purple-100 text-purple-800">{unassignedTweets.length}</Badge>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Auteur</TableHead>
                    <TableHead>Contenu</TableHead>
                    <TableHead>Priorité</TableHead>
                    <TableHead>Catégorie</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {unassignedTweets.slice(0, 3).map(tweet => (
                    <TableRow key={tweet.id} className="cursor-pointer hover:bg-gray-50" onClick={() => onTweetSelect(tweet)}>
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
                        <Button size="sm" variant="outline">Assigner</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}

          {/* Tweets urgents */}
          {urgentTweets.length > 0 && (
            <Card className="p-4 border-red-200">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <h3 className="text-gray-700">Urgences à traiter</h3>
                <Badge className="bg-red-100 text-red-800">{urgentTweets.length}</Badge>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Auteur</TableHead>
                    <TableHead>Contenu</TableHead>
                    <TableHead>Catégorie</TableHead>
                    <TableHead>Temps écoulé</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {urgentTweets.slice(0, 3).map(tweet => {
                    const minutes = Math.floor((Date.now() - tweet.timestamp.getTime()) / 1000 / 60);
                    return (
                      <TableRow key={tweet.id} className="cursor-pointer hover:bg-gray-50" onClick={() => onTweetSelect(tweet)}>
                        <TableCell>{tweet.author}</TableCell>
                        <TableCell className="max-w-md truncate">{tweet.content}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{tweet.category}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-red-100 text-red-800">{minutes}m</Badge>
                        </TableCell>
                        <TableCell>
                          <Button size="sm" className="bg-red-600 hover:bg-red-700">Traiter</Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </Card>
          )}
        </div>

        {/* Tous les tweets */}
        <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as any)} className="flex-1 flex flex-col">
          <TabsList className="bg-white border w-full justify-start rounded-none">
            <TabsTrigger value="all">
              Tous
            </TabsTrigger>
            <TabsTrigger value="unassigned">
              Restants ({unassignedTweets.length})
            </TabsTrigger>
            <TabsTrigger value="assigned">
              Assignés ({assignedCount})
            </TabsTrigger>
            <TabsTrigger value="in-progress">
              En cours ({inProgressCount})
            </TabsTrigger>
          </TabsList>

          <TabsContent value={statusFilter} className="mt-4">
            <div className="space-y-3">
              {filteredTweets.map((tweet) => (
                <TweetCard
                  key={tweet.id}
                  tweet={tweet}
                  onClick={() => onTweetSelect(tweet)}
                />
              ))}
              {filteredTweets.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  Aucun tweet trouvé
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

interface TweetCardProps {
  tweet: Tweet;
  onClick: () => void;
}

function TweetCard({ tweet, onClick }: TweetCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-orange-100 text-orange-800';
      case 'in-progress': return 'bg-blue-100 text-blue-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      default: return '😐';
    }
  };

  const getTimeAgo = (date: Date) => {
    const minutes = Math.floor((Date.now() - date.getTime()) / 1000 / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    return `${Math.floor(hours / 24)}j`;
  };

  return (
    <Card
      className="p-4 hover:shadow-md transition-shadow cursor-pointer border-l-4"
      style={{
        borderLeftColor: tweet.priority === 'high' ? '#ef4444' : 
                        tweet.priority === 'medium' ? '#f59e0b' : '#10b981'
      }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white">
            {tweet.author.charAt(0)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span>{tweet.author}</span>
              <span className="text-gray-500">{tweet.handle}</span>
              <span className="text-gray-400">· {getTimeAgo(tweet.timestamp)}</span>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={getStatusColor(tweet.status)}>
                {tweet.status === 'pending' ? 'En attente' : 
                 tweet.status === 'in-progress' ? 'En cours' : 'Résolu'}
              </Badge>
              <Badge className={getPriorityColor(tweet.priority)}>
                {tweet.priority === 'high' ? 'Haute' : 
                 tweet.priority === 'medium' ? 'Moyenne' : 'Basse'}
              </Badge>
              <Badge variant="outline">{tweet.category}</Badge>
              {tweet.confidence && tweet.confidence < 90 && (
                <Badge className="bg-orange-100 text-orange-800">
                  {tweet.confidence}% confiance
                </Badge>
              )}
              <span>{getSentimentIcon(tweet.sentiment)}</span>
            </div>
          </div>
        </div>
        <MessageCircle className="w-5 h-5 text-gray-400" />
      </div>
      <p className="text-gray-700 mt-2">{tweet.content}</p>
    </Card>
  );
}
