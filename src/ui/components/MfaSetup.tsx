import React, { useState, useEffect } from 'react';
import { useMfaApi, MfaSetupData } from '../../api/controllers/mfaApi';
import { Button, Input, Heading, Text, Box, Image, VStack, HStack, PinInput, PinInputField, useToast, Code, ListItem, UnorderedList, useClipboard } from '@chakra-ui/react';

interface MfaSetupProps {
    userId: string;
    onSetupComplete: () => void;
}

const MfaSetup: React.FC<MfaSetupProps> = ({ userId, onSetupComplete }) => {
    const [step, setStep] = useState<'setup' | 'verify'>('setup');
    const [mfaData, setMfaData] = useState<MfaSetupData | null>(null);
    const [verificationCode, setVerificationCode] = useState('');
    const [showBackupCodes, setShowBackupCodes] = useState(false);
    const { hasCopied, onCopy } = useClipboard('');
    const toast = useToast();

    const { useSetupMfa, useEnableMfa } = useMfaApi();
    const setupMfaMutation = useSetupMfa();
    const enableMfaMutation = useEnableMfa();

    // Initialize MFA setup
    useEffect(() => {
        setupMfaMutation.mutate(userId, {
            onSuccess: (data) => {
                setMfaData(data);
            },
            onError: (error) => {
                toast({
                    title: 'Error setting up MFA',
                    description: error instanceof Error ? error.message : 'An error occurred',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            },
        });
    }, [userId, setupMfaMutation, toast]);

    // Handle verification
    const handleVerification = () => {
        if (!verificationCode || verificationCode.length !== 6) {
            toast({
                title: 'Invalid code',
                description: 'Please enter a valid 6-digit verification code',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        enableMfaMutation.mutate({ userId, token: verificationCode }, {
            onSuccess: () => {
                toast({
                    title: 'MFA Enabled',
                    description: 'Multi-factor authentication has been successfully enabled',
                    status: 'success',
                    duration: 5000,
                    isClosable: true,
                });
                setShowBackupCodes(true);
            },
            onError: (error) => {
                toast({
                    title: 'Verification failed',
                    description: error instanceof Error ? error.message : 'Invalid verification code',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            },
        });
    };

    // Handle completion
    const handleComplete = () => {
        onSetupComplete();
    };

    // Copy backup codes
    const copyBackupCodes = () => {
        if (mfaData?.backup_codes) {
            const codes = mfaData.backup_codes.join('\n');
            navigator.clipboard.writeText(codes);
            toast({
                title: 'Backup codes copied',
                description: 'Please store these in a secure location',
                status: 'info',
                duration: 3000,
                isClosable: true,
            });
        }
    };

    if (!mfaData) {
        return <Box p={4}>Loading MFA setup...</Box>;
    }

    return (
        <Box p={6} borderWidth="1px" borderRadius="lg" boxShadow="md" maxW="600px" mx="auto">
            {!showBackupCodes ? (
                <>
                    <Heading size="lg" mb={4}>
                        {step === 'setup' ? 'Set Up Multi-Factor Authentication' : 'Verify Your Authenticator App'}
                    </Heading>

                    {step === 'setup' ? (
                        <VStack spacing={6} align="stretch">
                            <Text>
                                Multi-factor authentication adds an extra layer of security to your account.
                                After you enter your password, you'll need to provide a code from your
                                authenticator app.
                            </Text>

                            <Box textAlign="center">
                                <Text fontWeight="bold" mb={2}>Scan this QR code with your authenticator app:</Text>
                                {mfaData.qrcode && (
                                    <Image
                                        src={mfaData.qrcode}
                                        alt="QR Code for MFA setup"
                                        maxW="200px"
                                        mx="auto"
                                        border="1px solid"
                                        borderColor="gray.200"
                                    />
                                )}
                            </Box>

                            <Box>
                                <Text fontWeight="bold" mb={2}>Or enter this code manually:</Text>
                                <Code p={2} borderRadius="md" fontSize="md" bg="gray.100" mb={4}>
                                    {mfaData.secret}
                                </Code>
                            </Box>

                            <Button colorScheme="blue" onClick={() => setStep('verify')}>
                                Next: Verify Setup
                            </Button>
                        </VStack>
                    ) : (
                        <VStack spacing={6} align="stretch">
                            <Text>
                                Enter the 6-digit verification code from your authenticator app to confirm setup.
                            </Text>

                            <HStack justifyContent="center" mb={4}>
                                <PinInput type="number" size="lg" onChange={setVerificationCode}>
                                    <PinInputField />
                                    <PinInputField />
                                    <PinInputField />
                                    <PinInputField />
                                    <PinInputField />
                                    <PinInputField />
                                </PinInput>
                            </HStack>

                            <HStack justifyContent="space-between">
                                <Button variant="outline" onClick={() => setStep('setup')}>
                                    Back
                                </Button>
                                <Button
                                    colorScheme="blue"
                                    onClick={handleVerification}
                                    isLoading={enableMfaMutation.isPending}
                                >
                                    Verify and Enable MFA
                                </Button>
                            </HStack>
                        </VStack>
                    )}
                </>
            ) : (
                <VStack spacing={6} align="stretch">
                    <Heading size="lg" mb={4}>Backup Codes</Heading>

                    <Text>
                        These backup codes can be used to log in if you lose access to your authenticator app.
                        Each code can only be used once.
                    </Text>

                    <Box bg="gray.50" p={4} borderRadius="md" borderWidth="1px">
                        <UnorderedList spacing={2}>
                            {mfaData.backup_codes.map((code, index) => (
                                <ListItem key={index} fontFamily="mono">
                                    {code}
                                </ListItem>
                            ))}
                        </UnorderedList>
                    </Box>

                    <Text fontSize="sm" color="red.500" fontWeight="bold">
                        Important: Store these codes in a secure location. They will not be shown again.
                    </Text>

                    <HStack>
                        <Button colorScheme="blue" variant="outline" onClick={copyBackupCodes}>
                            Copy Codes
                        </Button>
                        <Button colorScheme="green" onClick={handleComplete}>
                            Complete Setup
                        </Button>
                    </HStack>
                </VStack>
            )}
        </Box>
    );
};

export default MfaSetup; 