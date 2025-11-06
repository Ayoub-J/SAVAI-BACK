import React from "react";
import { ArrowLeft, Settings, User, Bell, Lock, Palette } from "lucide-react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Switch } from "../ui/switch";
import { Label } from "../ui/label";

interface TwitterSettingsProps {
  onBack: () => void;
  onViewBackoffice: () => void;
}

export default function TwitterSettings({ onBack, onViewBackoffice }: TwitterSettingsProps) {
  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b p-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-[#e20e18]">Paramètres</h1>
            <p className="text-gray-600">Gérer vos préférences</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Profile Settings */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <User className="w-5 h-5 text-blue-600" />
            <h3 className="text-gray-700">Profil</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Nom d'affichage</Label>
                <p className="text-gray-500 text-sm">Agent Support</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Email</Label>
                <p className="text-gray-500 text-sm">agent@example.com</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Notification Settings */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="w-5 h-5 text-green-600" />
            <h3 className="text-gray-700">Notifications</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Nouveaux tweets</Label>
                <p className="text-gray-500 text-sm">Recevoir une notification pour chaque nouveau tweet</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Tweets urgents</Label>
                <p className="text-gray-500 text-sm">Alertes pour les tweets haute priorité</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Mentions</Label>
                <p className="text-gray-500 text-sm">Notifications pour les mentions directes</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </Card>

        {/* Appearance Settings */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Palette className="w-5 h-5 text-purple-600" />
            <h3 className="text-gray-700">Apparence</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Mode sombre</Label>
                <p className="text-gray-500 text-sm">Activer le thème sombre</p>
              </div>
              <Switch />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Mode compact</Label>
                <p className="text-gray-500 text-sm">Affichage condensé des tweets</p>
              </div>
              <Switch />
            </div>
          </div>
        </Card>

        {/* Backoffice Access */}
        <Card className="p-6 border-l-4 border-l-[#e20e18]">
          <div className="flex items-center gap-3 mb-4">
            <Settings className="w-5 h-5 text-[#e20e18]" />
            <h3 className="text-gray-700">Configuration technique</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Accéder aux paramètres avancés du backoffice pour configurer les modèles LLM,
            les seuils de confiance et les règles d'automatisation.
          </p>
          <Button
            onClick={onViewBackoffice}
            className="bg-[#e20e18] hover:bg-[#c00e15]"
          >
            <Settings className="w-4 h-4 mr-2" />
            Ouvrir la configuration backoffice
          </Button>
        </Card>

        {/* Privacy Settings */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Lock className="w-5 h-5 text-orange-600" />
            <h3 className="text-gray-700">Confidentialité</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Partage de données analytiques</Label>
                <p className="text-gray-500 text-sm">Contribuer aux statistiques anonymes</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Enregistrer l'historique</Label>
                <p className="text-gray-500 text-sm">Conserver l'historique des conversations</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
