import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Dice1, Dice2, Dice3, Dice4, Dice5, Dice6, 
  Eye, EyeOff, Target, TrendingUp, TrendingDown,
  Users, Clock, Zap, Shield, CheckCircle, XCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface Character {
  uuid: string;
  name: string;
  level: number;
  stats: Record<string, number>;
  skills: Record<string, {
    proficient: boolean;
    expertise: boolean;
    bonus: number;
  }>;
}

interface SkillCheckResult {
  skill_name: string;
  character_id: string;
  base_roll: number | number[];
  skill_modifier: number;
  final_modifiers: number;
  total_roll: number;
  dc?: number;
  success?: boolean;
  degree_of_success: number;
  critical_success: boolean;
  critical_failure: boolean;
  advantage_type: 'normal' | 'advantage' | 'disadvantage';
  description: string;
  timestamp: string;
}

interface SkillCheckOption {
  skill_name: string;
  option_text: string;
  dc: number;
  modifiers: number[];
  environmental_conditions: string[];
  description: string;
}

interface SkillCheckDialogProps {
  isOpen: boolean;
  onClose: () => void;
  character: Character;
  skillOptions: SkillCheckOption[];
  environmentalConditions: string[];
  onSkillCheck: (skill: string, modifiers: any) => Promise<SkillCheckResult>;
}

// Utility Components
const DiceIcon = ({ value }: { value: number }) => {
  const diceComponents = [Dice1, Dice2, Dice3, Dice4, Dice5, Dice6];
  const DiceComponent = value >= 1 && value <= 6 ? diceComponents[value - 1] : Dice6;
  return <DiceComponent className="w-8 h-8" />;
};

const DiceRollingAnimation = ({ 
  finalValue, 
  isRolling, 
  advantage 
}: { 
  finalValue: number | number[]; 
  isRolling: boolean;
  advantage: 'normal' | 'advantage' | 'disadvantage';
}) => {
  const [currentValue, setCurrentValue] = useState(1);
  
  useEffect(() => {
    if (isRolling) {
      const interval = setInterval(() => {
        setCurrentValue(Math.floor(Math.random() * 20) + 1);
      }, 100);
      
      const timeout = setTimeout(() => {
        clearInterval(interval);
        setCurrentValue(Array.isArray(finalValue) ? finalValue[0] : finalValue);
      }, 2000);
      
      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }
  }, [isRolling, finalValue]);
  
  const rolls = Array.isArray(finalValue) ? finalValue : [finalValue];
  const displayValue = isRolling ? currentValue : (Array.isArray(finalValue) ? finalValue : [finalValue]);
  
  return (
    <div className="flex items-center justify-center space-x-4">
      {advantage !== 'normal' && (
        <div className="flex space-x-2">
          {displayValue.map((roll, index) => (
            <motion.div
              key={index}
              className={`w-16 h-16 rounded-lg border-2 flex items-center justify-center text-2xl font-bold
                ${roll === 20 ? 'bg-green-100 border-green-500 text-green-700' : 
                  roll === 1 ? 'bg-red-100 border-red-500 text-red-700' : 
                  'bg-white border-gray-300'}
                ${advantage === 'advantage' && index === 0 ? 'ring-2 ring-blue-400' : ''}
                ${advantage === 'disadvantage' && index === 1 ? 'ring-2 ring-red-400' : ''}
              `}
              animate={isRolling ? { rotateY: 360 } : {}}
              transition={{ duration: 0.3, repeat: isRolling ? Infinity : 0 }}
            >
              {roll}
            </motion.div>
          ))}
        </div>
      )}
      
      {advantage === 'normal' && (
        <motion.div
          className={`w-20 h-20 rounded-lg border-2 flex items-center justify-center text-3xl font-bold
            ${displayValue[0] === 20 ? 'bg-green-100 border-green-500 text-green-700' : 
              displayValue[0] === 1 ? 'bg-red-100 border-red-500 text-red-700' : 
              'bg-white border-gray-300'}
          `}
          animate={isRolling ? { rotateY: 360 } : {}}
          transition={{ duration: 0.3, repeat: isRolling ? Infinity : 0 }}
        >
          {displayValue[0]}
        </motion.div>
      )}
      
      {advantage !== 'normal' && (
        <div className="text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            {advantage === 'advantage' ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500" />
            )}
            <span>{advantage === 'advantage' ? 'Advantage' : 'Disadvantage'}</span>
          </div>
          <div className="text-xs mt-1">
            Using: {advantage === 'advantage' ? 'Higher' : 'Lower'} roll
          </div>
        </div>
      )}
    </div>
  );
};

const EnvironmentalConditionBadge = ({ condition }: { condition: string }) => {
  const getConditionStyle = (condition: string) => {
    if (condition.includes('light') || condition.includes('bright')) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
    if (condition.includes('dark') || condition.includes('dim')) {
      return 'bg-gray-100 text-gray-800 border-gray-200';
    }
    if (condition.includes('rain') || condition.includes('storm')) {
      return 'bg-blue-100 text-blue-800 border-blue-200';
    }
    if (condition.includes('cover') || condition.includes('hidden')) {
      return 'bg-green-100 text-green-800 border-green-200';
    }
    return 'bg-gray-100 text-gray-600 border-gray-200';
  };
  
  return (
    <Badge variant="outline" className={getConditionStyle(condition)}>
      {condition.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
    </Badge>
  );
};

const SkillModifierBreakdown = ({ 
  skillModifier, 
  finalModifiers, 
  environmentalConditions 
}: { 
  skillModifier: number;
  finalModifiers: number;
  environmentalConditions: string[];
}) => {
  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="text-sm">Modifier Breakdown</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Base Skill Modifier:</span>
          <span className="font-mono">{skillModifier >= 0 ? '+' : ''}{skillModifier}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Environmental Modifiers:</span>
          <span className="font-mono">{finalModifiers >= 0 ? '+' : ''}{finalModifiers}</span>
        </div>
        <div className="border-t pt-2 flex justify-between font-semibold">
          <span>Total Modifier:</span>
          <span className="font-mono">{(skillModifier + finalModifiers) >= 0 ? '+' : ''}{skillModifier + finalModifiers}</span>
        </div>
        
        {environmentalConditions.length > 0 && (
          <div className="mt-3">
            <div className="text-xs text-gray-500 mb-1">Environmental Conditions:</div>
            <div className="flex flex-wrap gap-1">
              {environmentalConditions.map((condition, index) => (
                <EnvironmentalConditionBadge key={index} condition={condition} />
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const SkillCheckResult = ({ result }: { result: SkillCheckResult }) => {
  const getResultColor = () => {
    if (result.critical_success) return 'text-green-600';
    if (result.critical_failure) return 'text-red-600';
    if (result.success) return 'text-blue-600';
    return 'text-gray-600';
  };
  
  const getResultIcon = () => {
    if (result.critical_success) return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (result.critical_failure) return <XCircle className="w-5 h-5 text-red-500" />;
    if (result.success) return <CheckCircle className="w-5 h-5 text-blue-500" />;
    return <XCircle className="w-5 h-5 text-gray-500" />;
  };
  
  const getResultText = () => {
    if (result.critical_success) return 'Critical Success!';
    if (result.critical_failure) return 'Critical Failure!';
    if (result.success) return 'Success!';
    return 'Failure';
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 p-4 rounded-lg border bg-white"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getResultIcon()}
          <span className={`font-semibold ${getResultColor()}`}>
            {getResultText()}
          </span>
        </div>
        
        <div className="text-right">
          <div className="text-lg font-bold">
            {result.total_roll} {result.dc ? `vs DC ${result.dc}` : ''}
          </div>
          <div className="text-xs text-gray-500">
            Degree: {result.degree_of_success >= 0 ? '+' : ''}{result.degree_of_success}
          </div>
        </div>
      </div>
      
      <div className="text-sm text-gray-600">
        {result.description}
      </div>
      
      {(result.critical_success || result.critical_failure) && (
        <div className="mt-2 p-2 rounded bg-gray-50 text-xs text-gray-600">
          {result.critical_success && "Exceptional outcome! Additional benefits may apply."}
          {result.critical_failure && "Significant complications may arise from this failure."}
        </div>
      )}
    </motion.div>
  );
};

// Main Component
export const SkillCheckDialog: React.FC<SkillCheckDialogProps> = ({
  isOpen,
  onClose,
  character,
  skillOptions,
  environmentalConditions,
  onSkillCheck
}) => {
  const [selectedSkill, setSelectedSkill] = useState<SkillCheckOption | null>(null);
  const [isRolling, setIsRolling] = useState(false);
  const [result, setResult] = useState<SkillCheckResult | null>(null);
  const [activeTab, setActiveTab] = useState('select');
  
  const handleSkillSelect = (skill: SkillCheckOption) => {
    setSelectedSkill(skill);
    setActiveTab('confirm');
  };
  
  const handleRoll = async () => {
    if (!selectedSkill) return;
    
    setIsRolling(true);
    setActiveTab('rolling');
    
    try {
      const rollResult = await onSkillCheck(selectedSkill.skill_name, {
        environmental_conditions: selectedSkill.environmental_conditions,
        dc: selectedSkill.dc
      });
      
      // Wait for animation to complete
      setTimeout(() => {
        setResult(rollResult);
        setIsRolling(false);
        setActiveTab('result');
      }, 2500);
      
    } catch (error) {
      console.error('Skill check failed:', error);
      setIsRolling(false);
      setActiveTab('select');
    }
  };
  
  const handleClose = () => {
    setSelectedSkill(null);
    setResult(null);
    setActiveTab('select');
    setIsRolling(false);
    onClose();
  };
  
  const getSkillModifier = (skillName: string) => {
    const skillInfo = character.skills[skillName] || { proficient: false, expertise: false, bonus: 0 };
    const abilityMap: Record<string, string> = {
      'perception': 'wisdom',
      'stealth': 'dexterity',
      'persuasion': 'charisma',
      'investigation': 'intelligence',
      'athletics': 'strength'
    };
    
    const abilityName = abilityMap[skillName] || 'dexterity';
    const abilityScore = character.stats[abilityName] || 10;
    const abilityMod = Math.floor((abilityScore - 10) / 2);
    const proficiencyBonus = Math.floor((character.level - 1) / 4) + 2;
    
    let skillMod = abilityMod;
    if (skillInfo.proficient) {
      skillMod += proficiencyBonus;
      if (skillInfo.expertise) {
        skillMod += proficiencyBonus;
      }
    }
    skillMod += skillInfo.bonus;
    
    return skillMod;
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Target className="w-5 h-5" />
            <span>Skill Check - {character.name}</span>
          </DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="select" disabled={isRolling}>Select Skill</TabsTrigger>
            <TabsTrigger value="confirm" disabled={!selectedSkill || isRolling}>Confirm</TabsTrigger>
            <TabsTrigger value="rolling" disabled={!isRolling}>Rolling</TabsTrigger>
            <TabsTrigger value="result" disabled={!result}>Result</TabsTrigger>
          </TabsList>
          
          <TabsContent value="select" className="mt-4">
            <div className="space-y-3">
              <div className="text-sm text-gray-600 mb-4">
                Choose a skill to use in this situation:
              </div>
              
              {skillOptions.map((option, index) => {
                const skillMod = getSkillModifier(option.skill_name);
                return (
                  <Card 
                    key={index}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => handleSkillSelect(option)}
                  >
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-base capitalize">
                          {option.skill_name.replace(/_/g, ' ')}
                        </CardTitle>
                        <div className="text-right">
                          <div className="text-lg font-bold">DC {option.dc}</div>
                          <div className="text-xs text-gray-500">
                            Your Modifier: {skillMod >= 0 ? '+' : ''}{skillMod}
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-sm">
                        {option.option_text}
                      </CardDescription>
                      
                      {option.environmental_conditions.length > 0 && (
                        <div className="mt-2">
                          <div className="text-xs text-gray-500 mb-1">Conditions:</div>
                          <div className="flex flex-wrap gap-1">
                            {option.environmental_conditions.map((condition, idx) => (
                              <EnvironmentalConditionBadge key={idx} condition={condition} />
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
          
          <TabsContent value="confirm" className="mt-4">
            {selectedSkill && (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="capitalize">
                      {selectedSkill.skill_name.replace(/_/g, ' ')} Check
                    </CardTitle>
                    <CardDescription>
                      {selectedSkill.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-lg font-semibold">Difficulty Class:</span>
                      <span className="text-2xl font-bold">DC {selectedSkill.dc}</span>
                    </div>
                    
                    <SkillModifierBreakdown
                      skillModifier={getSkillModifier(selectedSkill.skill_name)}
                      finalModifiers={selectedSkill.modifiers.reduce((a, b) => a + b, 0)}
                      environmentalConditions={selectedSkill.environmental_conditions}
                    />
                  </CardContent>
                </Card>
                
                <div className="flex space-x-3">
                  <Button onClick={() => setActiveTab('select')} variant="outline" className="flex-1">
                    Back
                  </Button>
                  <Button onClick={handleRoll} className="flex-1">
                    <Dice6 className="w-4 h-4 mr-2" />
                    Roll d20
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="rolling" className="mt-4">
            <div className="text-center py-8">
              <div className="mb-6">
                <h3 className="text-xl font-semibold mb-2">
                  Rolling {selectedSkill?.skill_name.replace(/_/g, ' ')} Check...
                </h3>
                <div className="text-gray-600">
                  DC {selectedSkill?.dc}
                </div>
              </div>
              
              <DiceRollingAnimation
                finalValue={result?.base_roll || 10}
                isRolling={isRolling}
                advantage={result?.advantage_type || 'normal'}
              />
              
              <div className="mt-6">
                <Progress value={isRolling ? 60 : 100} className="w-full" />
                <div className="text-sm text-gray-500 mt-2">
                  {isRolling ? 'Rolling...' : 'Complete!'}
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="result" className="mt-4">
            {result && selectedSkill && (
              <div>
                <SkillCheckResult result={result} />
                
                <SkillModifierBreakdown
                  skillModifier={result.skill_modifier}
                  finalModifiers={result.final_modifiers}
                  environmentalConditions={selectedSkill.environmental_conditions}
                />
                
                <div className="mt-6 flex space-x-3">
                  <Button onClick={handleClose} className="flex-1">
                    Close
                  </Button>
                  <Button 
                    onClick={() => {
                      setResult(null);
                      setSelectedSkill(null);
                      setActiveTab('select');
                    }} 
                    variant="outline" 
                    className="flex-1"
                  >
                    New Check
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default SkillCheckDialog; 