import React, { useMemo, useCallback, useState } from 'react';
import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Button,
    Progress,
    useToast,
    Box,
    Text,
    VStack,
    HStack,
    IconButton,
    useDisclosure,
} from '@chakra-ui/react';
import { InfoIcon, WarningIcon, CloseIcon } from '@chakra-ui/icons';
import { useInteractionStore, InterruptionState, InterruptionMeta, selectInterruptionConfig } from '../../../store/core/interactionStore';
import { RecoveryOrchestrator } from '../../../core/utils/recoveryOrchestrator';

/**
 * Interruption types
 */
export type InterruptionType = 'pause' | 'error' | 'exit';

/**
 * Props for InterruptionNotification
 */
export interface InterruptionNotificationProps {
    type: InterruptionType;
    message: string;
    isOpen: boolean;
    onClose: () => void;
    onRetry?: () => void;
    onCancel?: () => void;
    onContinue?: () => void;
    progress?: number | null;
    isLoading?: boolean;
}

/**
 * InterruptionNotification component displays interruption status and controls
 */
export const InterruptionNotification: React.FC<InterruptionNotificationProps> = ({
    type,
    message,
    isOpen,
    onClose,
    onRetry,
    onCancel,
    onContinue,
    progress = null,
    isLoading = false,
}) => {
    const toast = useToast();
    const { isOpen: isFeedbackOpen, onOpen: openFeedback, onClose: closeFeedback } = useDisclosure();

    // Icon and color by type
    const icon = type === 'error' ? <WarningIcon color="red.500" boxSize={6} /> : <InfoIcon color="blue.500" boxSize={6} />;
    const header =
        type === 'pause'
            ? 'Session Paused'
            : type === 'error'
                ? 'System Error'
                : 'Session Ended';

    // Feedback modal stub
    const FeedbackModal = (
        <Modal isOpen={isFeedbackOpen} onClose={closeFeedback} isCentered>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Send Feedback</ModalHeader>
                <ModalBody>
                    <Text mb={4}>Let us know what happened or how we can improve interruption handling.</Text>
                    {/* TODO: Add feedback form */}
                    <Button colorScheme="blue" onClick={closeFeedback} width="full">
                        Close
                    </Button>
                </ModalBody>
            </ModalContent>
        </Modal>
    );

    return (
        <>
            <Modal isOpen={isOpen} onClose={onClose} isCentered motionPreset="scale">
                <ModalOverlay />
                <ModalContent role="alertdialog" aria-modal="true" aria-labelledby="interruption-header">
                    <ModalHeader id="interruption-header">
                        <HStack spacing={3}>
                            {icon}
                            <Text>{header}</Text>
                        </HStack>
                    </ModalHeader>
                    <ModalBody>
                        <VStack align="stretch" spacing={4}>
                            <Text>{message}</Text>
                            {progress !== null && (
                                <Progress value={progress} size="sm" colorScheme="blue" isIndeterminate={progress === 0} />
                            )}
                        </VStack>
                    </ModalBody>
                    <ModalFooter>
                        <HStack spacing={2} width="100%" justify="space-between">
                            <HStack spacing={2}>
                                {onRetry && (
                                    <Button onClick={onRetry} colorScheme="blue" isLoading={isLoading} aria-label="Retry">
                                        Retry
                                    </Button>
                                )}
                                {onContinue && (
                                    <Button onClick={onContinue} colorScheme="green" isLoading={isLoading} aria-label="Continue">
                                        Continue
                                    </Button>
                                )}
                                {onCancel && (
                                    <Button onClick={onCancel} colorScheme="red" variant="outline" isLoading={isLoading} aria-label="Cancel">
                                        Cancel
                                    </Button>
                                )}
                            </HStack>
                            <IconButton
                                icon={<CloseIcon />}
                                aria-label="Close"
                                onClick={onClose}
                                variant="ghost"
                                size="sm"
                            />
                            <Button onClick={openFeedback} variant="link" colorScheme="blue" ml={2} aria-label="Send Feedback">
                                Feedback
                            </Button>
                        </HStack>
                    </ModalFooter>
                </ModalContent>
            </Modal>
            {FeedbackModal}
        </>
    );
};

/**
 * Container component that wires InterruptionNotification to the store and orchestrator
 */
const InterruptionNotificationContainer: React.FC = () => {
    const interruptionState = useInteractionStore((s) => s.interruptionState);
    const interruptionMeta = useInteractionStore((s) => s.interruptionMeta);
    const config = selectInterruptionConfig();
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState<number | null>(null);
    const orchestrator = useMemo(() => new RecoveryOrchestrator({
        maxRetries: config.maxRetries,
        baseInterval: config.baseIntervalMs,
    }), [config.maxRetries, config.baseIntervalMs]);

    // Map interruption state to notification type
    const type: InterruptionType =
        interruptionState === InterruptionState.TEMPORARY_PAUSE ? 'pause' :
            interruptionState === InterruptionState.SYSTEM_ERROR ? 'error' :
                interruptionState === InterruptionState.USER_EXIT ? 'exit' : 'pause';

    // Message and controls
    const message = interruptionMeta?.event || 'Session interrupted.';
    const isOpen = interruptionState !== InterruptionState.NONE;

    // Handlers
    const handleRetry = useCallback(async () => {
        setIsLoading(true);
        setProgress(0);
        try {
            const result = await orchestrator.recover({
                interruptionState,
                interruptionMeta,
                preservedContext: {}, // TODO: wire actual context
            });
            setProgress(100);
            // TODO: update store with recovery result
        } finally {
            setIsLoading(false);
            setProgress(null);
        }
    }, [orchestrator, interruptionState, interruptionMeta]);

    const handleCancel = useCallback(() => {
        // TODO: dispatch cancel action to store
    }, []);

    const handleContinue = useCallback(() => {
        // TODO: dispatch continue action to store
    }, []);

    const handleClose = useCallback(() => {
        // TODO: clear interruption state in store
    }, []);

    return (
        <InterruptionNotification
            type={type}
            message={message}
            isOpen={isOpen}
            onRetry={handleRetry}
            onCancel={handleCancel}
            onContinue={handleContinue}
            onClose={handleClose}
            progress={progress}
            isLoading={isLoading}
        />
    );
};

export default InterruptionNotificationContainer; 