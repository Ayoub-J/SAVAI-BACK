import React, { useState } from "react";
import { ArrowLeft, Settings, Cpu, Brain, Zap, Shield } from "lucide-react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Switch } from "../ui/switch";
import { Label } from "../ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Slider } from "../ui/slider";
import { Input } from "../ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";

interface TwitterBackofficeSettingsProps {
  onBack: () => void;
}

export default function TwitterBackofficeSettings({ onBack }: TwitterBackofficeSettingsProps) {
  const [llmModel, setLlmModel] = useState("gpt-4");
  const [confidenceThreshold, setConfidenceThreshold] = useState([75]);
  const [autoResponseEnabled, setAutoResponseEnabled] = useState(false);
  const [sentimentThreshold, setSentimentThreshold] = useState([80]);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b p-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-[#e20e18]">Configuration Backoffice</h1>
            <p className="text-gray-600">Paramètres techniques et automatisation</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <Tabs defaultValue="llm" className="space-y-6">
          <TabsList>
            <TabsTrigger value="llm">
              <Brain className="w-4 h-4 mr-2" />
              Modèle LLM
            </TabsTrigger>
            <TabsTrigger value="analysis">
              <Cpu className="w-4 h-4 mr-2" />
              Analyse
            </TabsTrigger>
            <TabsTrigger value="automation">
              <Zap className="w-4 h-4 mr-2" />
              Automatisation
            </TabsTrigger>
            <TabsTrigger value="security">
              <Shield className="w-4 h-4 mr-2" />
              Sécurité
            </TabsTrigger>
          </TabsList>

          <TabsContent value="llm" className="space-y-6">
            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Sélection du modèle LLM</h3>
              <div className="space-y-4">
                <div>
                  <Label>Modèle principal</Label>
                  <Select value={llmModel} onValueChange={setLlmModel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4">GPT-4 (Recommandé)</SelectItem>
                      <SelectItem value="gpt-3.5">GPT-3.5 Turbo</SelectItem>
                      <SelectItem value="claude">Claude 3</SelectItem>
                      <SelectItem value="mistral">Mistral Large</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-gray-500 text-sm mt-2">
                    Modèle utilisé pour la classification et l'analyse
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Paramètres du modèle</h3>
              <div className="space-y-4">
                <div>
                  <Label>Température (Créativité)</Label>
                  <Input type="number" defaultValue="0.7" step="0.1" min="0" max="1" />
                  <p className="text-gray-500 text-sm mt-2">
                    Plus élevé = réponses plus créatives
                  </p>
                </div>
                <div>
                  <Label>Max Tokens</Label>
                  <Input type="number" defaultValue="500" />
                  <p className="text-gray-500 text-sm mt-2">
                    Longueur maximale des réponses générées
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-6">
            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Seuils de confiance</h3>
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label>Seuil de confiance classification</Label>
                    <span className="text-sm">{confidenceThreshold[0]}%</span>
                  </div>
                  <Slider
                    value={confidenceThreshold}
                    onValueChange={setConfidenceThreshold}
                    min={0}
                    max={100}
                    step={5}
                  />
                  <p className="text-gray-500 text-sm mt-2">
                    Tweets sous ce seuil nécessitent une validation manuelle
                  </p>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label>Seuil de confiance sentiment</Label>
                    <span className="text-sm">{sentimentThreshold[0]}%</span>
                  </div>
                  <Slider
                    value={sentimentThreshold}
                    onValueChange={setSentimentThreshold}
                    min={0}
                    max={100}
                    step={5}
                  />
                  <p className="text-gray-500 text-sm mt-2">
                    Seuil pour l'analyse de sentiment automatique
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Catégories de classification</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Switch defaultChecked />
                    <Label>Panne Internet</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch defaultChecked />
                    <Label>Facturation</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch defaultChecked />
                    <Label>Espace Client</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch defaultChecked />
                    <Label>Fibre</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch defaultChecked />
                    <Label>Résiliation</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch defaultChecked />
                    <Label>Remerciement</Label>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="automation" className="space-y-6">
            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Réponses automatiques</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Activer les réponses automatiques</Label>
                    <p className="text-gray-500 text-sm">
                      Le système génère et envoie des réponses automatiquement
                    </p>
                  </div>
                  <Switch
                    checked={autoResponseEnabled}
                    onCheckedChange={setAutoResponseEnabled}
                  />
                </div>

                {autoResponseEnabled && (
                  <div className="pl-4 border-l-2 border-blue-500 space-y-4">
                    <div className="flex items-center space-x-2">
                      <Switch defaultChecked />
                      <Label>Remerciements</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch />
                      <Label>Questions fréquentes</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch />
                      <Label>Demandes d'information</Label>
                    </div>
                  </div>
                )}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Règles d'assignation</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Auto-assignation aux agents</Label>
                    <p className="text-gray-500 text-sm">
                      Assigner automatiquement selon la disponibilité
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Priorisation automatique</Label>
                    <p className="text-gray-500 text-sm">
                      Ajuster la priorité selon le contenu
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="security" className="space-y-6">
            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Sécurité et conformité</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Détection de données sensibles</Label>
                    <p className="text-gray-500 text-sm">
                      Alerter si des données personnelles sont détectées
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Anonymisation automatique</Label>
                    <p className="text-gray-500 text-sm">
                      Masquer les informations sensibles dans les logs
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Validation humaine requise</Label>
                    <p className="text-gray-500 text-sm">
                      Pour les réponses concernant des données sensibles
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-gray-700 mb-4">Audit et logs</h3>
              <div className="space-y-4">
                <div>
                  <Label>Durée de rétention des logs</Label>
                  <Select defaultValue="30">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7">7 jours</SelectItem>
                      <SelectItem value="30">30 jours</SelectItem>
                      <SelectItem value="90">90 jours</SelectItem>
                      <SelectItem value="365">1 an</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="mt-6 flex justify-end gap-4">
          <Button variant="outline" onClick={onBack}>
            Annuler
          </Button>
          <Button className="bg-[#e20e18] hover:bg-[#c00e15]">
            Enregistrer les modifications
          </Button>
        </div>
      </div>
    </div>
  );
}
