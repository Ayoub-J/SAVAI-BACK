import React, { useState } from "react";
import { ArrowLeft, Send, AlertCircle, CheckCircle, Clock } from "lucide-react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Badge } from "../ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

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
}

interface TwitterConversationProps {
  tweet: Tweet;
  onBack: () => void;
  onStatusChange: (status: Tweet['status']) => void;
}

export default function TwitterConversation({ tweet, onBack, onStatusChange }: TwitterConversationProps) {
  const [response, setResponse] = useState("");
  const [messages, setMessages] = useState([
    {
      id: '1',
      sender: 'user',
      content: tweet.content,
      timestamp: tweet.timestamp,
    }
  ]);

  const handleSendResponse = () => {
    if (response.trim()) {
      setMessages([
        ...messages,
        {
          id: Date.now().toString(),
          sender: 'agent',
          content: response,
          timestamp: new Date(),
        }
      ]);
      setResponse("");
      if (tweet.status === 'pending') {
        onStatusChange('in-progress');
      }
    }
  };

  const getPriorityColor = (priority: Tweet['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-700 border-green-200';
    }
  };

  const getSentimentColor = (sentiment: Tweet['sentiment']) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-700';
      case 'neutral':
        return 'bg-gray-100 text-gray-700';
      case 'negative':
        return 'bg-red-100 text-red-700';
    }
  };

  const getStatusIcon = (status: Tweet['status']) => {
    switch (status) {
      case 'pending':
        return <AlertCircle className="w-4 h-4" />;
      case 'in-progress':
        return <Clock className="w-4 h-4" />;
      case 'resolved':
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onBack}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-gray-900">{tweet.author}</h1>
              <p className="text-gray-600">{tweet.handle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getPriorityColor(tweet.priority)}>
              {tweet.priority === 'high' ? 'Haute' : tweet.priority === 'medium' ? 'Moyenne' : 'Basse'} priorité
            </Badge>
            <Badge variant="outline">{tweet.category}</Badge>
          </div>
        </div>
      </div>

      {/* Tweet Details */}
      <div className="bg-white border-b p-4">
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            {getStatusIcon(tweet.status)}
            <Select value={tweet.status} onValueChange={(value) => onStatusChange(value as Tweet['status'])}>
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pending">En attente</SelectItem>
                <SelectItem value="in-progress">En cours</SelectItem>
                <SelectItem value="resolved">Résolu</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Badge className={getSentimentColor(tweet.sentiment)} variant="outline">
            Sentiment: {tweet.sentiment === 'positive' ? 'Positif' : tweet.sentiment === 'neutral' ? 'Neutre' : 'Négatif'}
          </Badge>
        </div>
      </div>

      {/* Conversation */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'agent' ? 'justify-end' : 'justify-start'}`}
          >
            <Card
              className={`max-w-[70%] p-4 ${
                message.sender === 'agent'
                  ? 'bg-[#e20e18] text-white'
                  : 'bg-white'
              }`}
            >
              <p className={message.sender === 'agent' ? 'text-white' : 'text-gray-900'}>
                {message.content}
              </p>
              <p
                className={`text-xs mt-2 ${
                  message.sender === 'agent' ? 'text-white/70' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString('fr-FR', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </Card>
          </div>
        ))}
      </div>

      {/* Response Input */}
      <div className="bg-white border-t p-6">
        <div className="flex gap-4">
          <Textarea
            placeholder="Tapez votre réponse..."
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            className="flex-1"
            rows={3}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendResponse();
              }
            }}
          />
          <Button
            onClick={handleSendResponse}
            disabled={!response.trim()}
            className="bg-[#e20e18] hover:bg-[#c00e15]"
          >
            <Send className="w-4 h-4 mr-2" />
            Envoyer
          </Button>
        </div>
        <p className="text-gray-500 text-sm mt-2">
          Appuyez sur Entrée pour envoyer, Shift+Entrée pour une nouvelle ligne
        </p>
      </div>
    </div>
  );
}
