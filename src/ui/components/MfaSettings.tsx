import React, { useState } from 'react';
import { Box, Button, Heading, Text, Switch, FormControl, FormLabel, VStack, Divider, Alert, AlertIcon, useDisclosure, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalFooter, useToast } from '@chakra-ui/react';
import { useMfaApi } from '../../api/controllers/mfaApi';
import MfaSetup from './MfaSetup';

interface MfaSettingsProps {
    userId: string;
    userDetails: {
        mfaEnabled: boolean;
        paymentEnabled: boolean;
    };
    onStatusChange: () => void;
}

const MfaSettings: React.FC<MfaSettingsProps> = ({ userId, userDetails, onStatusChange }) => {
    const { isOpen, onOpen, onClose } = useDisclosure();
    const [setupMode, setSetupMode] = useState(false);
    const toast = useToast();

    const { useDisableMfa, useBackupCodes, useRegenerateBackupCodes } = useMfaApi();
    const disableMfaMutation = useDisableMfa();
    const { data: backupCodes } = useBackupCodes(userDetails.mfaEnabled ? userId : '');
    const regenerateBackupCodesMutation = useRegenerateBackupCodes();

    const handleSetupMfa = () => {
        setSetupMode(true);
    };

    const handleSetupComplete = () => {
        setSetupMode(false);
        onStatusChange();
        toast({
            title: 'MFA Enabled',
            description: 'Multi-factor authentication has been successfully set up',
            status: 'success',
            duration: 5000,
            isClosable: true,
        });
    };

    const handleDisableMfa = () => {
        if (userDetails.paymentEnabled) {
            toast({
                title: 'Cannot Disable MFA',
                description: 'MFA is required for accounts with payment capabilities',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
            return;
        }

        disableMfaMutation.mutate(userId, {
            onSuccess: () => {
                onClose();
                onStatusChange();
                toast({
                    title: 'MFA Disabled',
                    description: 'Multi-factor authentication has been turned off',
                    status: 'info',
                    duration: 5000,
                    isClosable: true,
                });
            },
            onError: (error) => {
                toast({
                    title: 'Error',
                    description: error instanceof Error ? error.message : 'Failed to disable MFA',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            },
        });
    };

    const handleRegenerateBackupCodes = () => {
        regenerateBackupCodesMutation.mutate(userId, {
            onSuccess: () => {
                toast({
                    title: 'Backup Codes Regenerated',
                    description: 'Your new backup codes are now available',
                    status: 'success',
                    duration: 5000,
                    isClosable: true,
                });
            },
            onError: (error) => {
                toast({
                    title: 'Error',
                    description: error instanceof Error ? error.message : 'Failed to regenerate backup codes',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            },
        });
    };

    // If in setup mode, show the MFA setup component
    if (setupMode) {
        return <MfaSetup userId={userId} onSetupComplete={handleSetupComplete} />;
    }

    return (
        <Box p={5} borderWidth="1px" borderRadius="lg" boxShadow="sm">
            <VStack spacing={5} align="stretch">
                <Heading size="md">Two-Factor Authentication</Heading>

                <Text>
                    Two-factor authentication adds an extra layer of security to your account by requiring
                    access to your phone in addition to your password when you log in.
                </Text>

                {userDetails.paymentEnabled && !userDetails.mfaEnabled && (
                    <Alert status="warning">
                        <AlertIcon />
                        MFA must be enabled for accounts with payment capabilities.
                    </Alert>
                )}

                <FormControl display="flex" alignItems="center">
                    <FormLabel htmlFor="mfa-toggle" mb="0">
                        Enable two-factor authentication
                    </FormLabel>
                    <Switch
                        id="mfa-toggle"
                        isChecked={userDetails.mfaEnabled}
                        onChange={userDetails.mfaEnabled ? onOpen : handleSetupMfa}
                        isDisabled={disableMfaMutation.isPending}
                    />
                </FormControl>

                {userDetails.mfaEnabled && (
                    <>
                        <Divider />

                        <Box>
                            <Heading size="sm" mb={3}>Backup Codes</Heading>
                            <Text mb={3}>
                                Backup codes can be used to access your account if you cannot receive
                                two-factor authentication codes.
                            </Text>
                            <Text fontSize="sm" fontStyle="italic" mb={3}>
                                Each backup code can only be used once.
                            </Text>

                            <Button
                                colorScheme="blue"
                                variant="outline"
                                onClick={handleRegenerateBackupCodes}
                                isLoading={regenerateBackupCodesMutation.isPending}
                                mr={3}
                            >
                                Regenerate Backup Codes
                            </Button>
                        </Box>
                    </>
                )}
            </VStack>

            {/* Confirmation Modal for Disabling MFA */}
            <Modal isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Disable Two-Factor Authentication?</ModalHeader>
                    <ModalBody>
                        <Text>
                            Turning off two-factor authentication will reduce the security of your account.
                            Are you sure you want to continue?
                        </Text>
                    </ModalBody>

                    <ModalFooter>
                        <Button variant="ghost" mr={3} onClick={onClose}>
                            Cancel
                        </Button>
                        <Button
                            colorScheme="red"
                            onClick={handleDisableMfa}
                            isLoading={disableMfaMutation.isPending}
                        >
                            Disable
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </Box>
    );
};

export default MfaSettings; 