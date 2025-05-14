import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, FormikHelpers } from 'formik';
import * as Yup from 'yup';
import { Button, FormControl, FormLabel, Input, FormErrorMessage, VStack, Heading, Box, useToast } from '@chakra-ui/react';
import MfaVerification from './MfaVerification';

// Import services
import { UserService } from '../../services/UserService';

interface LoginFormValues {
    email: string;
    password: string;
}

const LoginSchema = Yup.object().shape({
    email: Yup.string()
        .email('Invalid email address')
        .required('Email is required'),
    password: Yup.string()
        .required('Password is required')
        .min(12, 'Password must be at least 12 characters'),
});

const LoginForm: React.FC = () => {
    const [showMfa, setShowMfa] = useState(false);
    const [userId, setUserId] = useState<string>('');
    const navigate = useNavigate();
    const toast = useToast();
    const userService = new UserService();

    const handleSubmit = async (
        values: LoginFormValues,
        actions: FormikHelpers<LoginFormValues>
    ) => {
        try {
            const response = await userService.login(values.email, values.password);

            if (response.success) {
                const { user, token, requiresMfa } = response.data;

                // Store user ID for MFA verification
                setUserId(user.id);

                // Check if MFA is required
                if (requiresMfa) {
                    // Show MFA verification
                    setShowMfa(true);
                } else {
                    // No MFA required, proceed with login
                    completeLogin(token);
                }
            } else {
                toast({
                    title: 'Login failed',
                    description: response.error || 'Invalid credentials',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            }
        } catch (error) {
            toast({
                title: 'Login error',
                description: error instanceof Error ? error.message : 'An error occurred',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            actions.setSubmitting(false);
        }
    };

    const handleMfaComplete = (token: string) => {
        completeLogin(token);
    };

    const handleMfaCancel = () => {
        setShowMfa(false);
        // Clear any stored authentication data
        localStorage.removeItem('token');
    };

    const completeLogin = (token: string) => {
        // Store the authentication token
        localStorage.setItem('token', token);

        // Redirect to dashboard or home page
        navigate('/dashboard');

        toast({
            title: 'Login successful',
            status: 'success',
            duration: 3000,
            isClosable: true,
        });
    };

    // If MFA verification is required, show the MFA component
    if (showMfa) {
        return (
            <MfaVerification
                userId={userId}
                onVerificationComplete={handleMfaComplete}
                onCancel={handleMfaCancel}
            />
        );
    }

    return (
        <Box p={6} borderWidth="1px" borderRadius="lg" boxShadow="md" maxW="500px" mx="auto">
            <Heading size="lg" mb={6} textAlign="center">Login</Heading>

            <Formik
                initialValues={{
                    email: '',
                    password: '',
                }}
                validationSchema={LoginSchema}
                onSubmit={handleSubmit}
            >
                {({ isSubmitting, errors, touched }) => (
                    <Form>
                        <VStack spacing={4} align="flex-start">
                            <FormControl isInvalid={!!errors.email && touched.email}>
                                <FormLabel htmlFor="email">Email Address</FormLabel>
                                <Field
                                    as={Input}
                                    id="email"
                                    name="email"
                                    type="email"
                                    variant="filled"
                                    placeholder="your-email@example.com"
                                />
                                <FormErrorMessage>{errors.email}</FormErrorMessage>
                            </FormControl>

                            <FormControl isInvalid={!!errors.password && touched.password}>
                                <FormLabel htmlFor="password">Password</FormLabel>
                                <Field
                                    as={Input}
                                    id="password"
                                    name="password"
                                    type="password"
                                    variant="filled"
                                    placeholder="Enter your password"
                                />
                                <FormErrorMessage>{errors.password}</FormErrorMessage>
                            </FormControl>

                            <Button
                                type="submit"
                                colorScheme="blue"
                                width="full"
                                mt={4}
                                isLoading={isSubmitting}
                            >
                                Login
                            </Button>
                        </VStack>
                    </Form>
                )}
            </Formik>
        </Box>
    );
};

export default LoginForm; 