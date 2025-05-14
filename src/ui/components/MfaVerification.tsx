import React, { useState } from 'react';
import { useMfaApi } from '../../api/controllers/mfaApi';
import { Button, Text, Box, VStack, HStack, PinInput, PinInputField, useToast, Tabs, TabList, Tab, TabPanels, TabPanel, FormControl, FormLabel, Input } from '@chakra-ui/react';

interface MfaVerificationProps {
    userId: string;
    onVerificationComplete: (token: string) => void;
    onCancel: () => void;
}

const MfaVerification: React.FC<MfaVerificationProps> = ({
    userId,
    onVerificationComplete,
    onCancel
}) => {
    const [verificationCode, setVerificationCode] = useState('');
    const [backupCode, setBackupCode] = useState('');
    const [tabIndex, setTabIndex] = useState(0);
    const toast = useToast();

    const { useVerifyMfa } = useMfaApi();
    const verifyMfaMutation = useVerifyMfa();

    // Handle TOTP verification
    const handleTotpVerification = () => {
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

        verifyMfaMutation.mutate(
            { userId, token: verificationCode, isBackupCode: false },
            {
                onSuccess: (data) => {
                    onVerificationComplete(data.token);
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
            }
        );
    };

    // Handle backup code verification
    const handleBackupVerification = () => {
        if (!backupCode) {
            toast({
                title: 'Invalid code',
                description: 'Please enter a backup code',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        verifyMfaMutation.mutate(
            { userId, token: backupCode, isBackupCode: true },
            {
                onSuccess: (data) => {
                    onVerificationComplete(data.token);
                },
                onError: (error) => {
                    toast({
                        title: 'Verification failed',
                        description: error instanceof Error ? error.message : 'Invalid backup code',
                        status: 'error',
                        duration: 5000,
                        isClosable: true,
                    });
                },
            }
        );
    };

    return (
        <Box p={6} borderWidth="1px" borderRadius="lg" boxShadow="md" maxW="500px" mx="auto">
            <VStack spacing={6} align="stretch">
                <Text fontSize="xl" fontWeight="bold" textAlign="center">
                    Multi-Factor Authentication Required
                </Text>

                <Text>
                    Additional verification is required to access your account.
                    Please enter a verification code from your authenticator app or use a backup code.
                </Text>

                <Tabs isFitted variant="enclosed" index={tabIndex} onChange={setTabIndex}>
                    <TabList mb="1em">
                        <Tab>Authenticator App</Tab>
                        <Tab>Backup Code</Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel>
                            <VStack spacing={4}>
                                <Text>Enter the 6-digit code from your authenticator app:</Text>
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
                                <Button
                                    colorScheme="blue"
                                    width="full"
                                    onClick={handleTotpVerification}
                                    isLoading={verifyMfaMutation.isPending && tabIndex === 0}
                                >
                                    Verify
                                </Button>
                            </VStack>
                        </TabPanel>
                        <TabPanel>
                            <VStack spacing={4}>
                                <FormControl>
                                    <FormLabel>Enter a backup code:</FormLabel>
                                    <Input
                                        placeholder="XXXX-XXXX"
                                        value={backupCode}
                                        onChange={(e) => setBackupCode(e.target.value)}
                                        mb={4}
                                    />
                                </FormControl>
                                <Text fontSize="sm">
                                    Note: Each backup code can only be used once.
                                </Text>
                                <Button
                                    colorScheme="blue"
                                    width="full"
                                    onClick={handleBackupVerification}
                                    isLoading={verifyMfaMutation.isPending && tabIndex === 1}
                                >
                                    Verify with Backup Code
                                </Button>
                            </VStack>
                        </TabPanel>
                    </TabPanels>
                </Tabs>

                <Button variant="ghost" onClick={onCancel}>
                    Cancel
                </Button>
            </VStack>
        </Box>
    );
};

export default MfaVerification; 