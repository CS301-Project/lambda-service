package com.bank.crm;

import java.util.HashMap;
import java.util.Map;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.ApplicationLoadBalancerRequestEvent;
import com.amazonaws.services.lambda.runtime.events.ApplicationLoadBalancerResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;

import software.amazon.awssdk.services.cognitoidentityprovider.CognitoIdentityProviderClient;
import software.amazon.awssdk.services.cognitoidentityprovider.model.AdminCreateUserRequest;
import software.amazon.awssdk.services.cognitoidentityprovider.model.AdminCreateUserResponse;
import software.amazon.awssdk.services.cognitoidentityprovider.model.AttributeType;
import software.amazon.awssdk.services.cognitoidentityprovider.model.CognitoIdentityProviderException;

/**
 * Lambda function entry point for handling ALB requests to create users in
 * Cognito.
 *
 * @see <a
 *      href=https://docs.aws.amazon.com/lambda/latest/dg/java-handler.html>Lambda
 *      Java Handler</a> for more information
 */
public class App implements RequestHandler<ApplicationLoadBalancerRequestEvent, ApplicationLoadBalancerResponseEvent> {
    private final CognitoIdentityProviderClient cognitoIdentityProviderClient;
    private final ObjectMapper objectMapper;
    private final String userPoolId;

    public App() {
        // Initialize the SDK client outside of the handler method so that it can be
        // reused for subsequent invocations.
        cognitoIdentityProviderClient = DependencyFactory.cognitoIdentityProviderClient();
        objectMapper = new ObjectMapper();
        userPoolId = System.getenv("USER_POOL_ID");
    }

    @Override
    public ApplicationLoadBalancerResponseEvent handleRequest(final ApplicationLoadBalancerRequestEvent input,
            final Context context) {
        context.getLogger().log("Received ALB request: " + input.getPath());

        ApplicationLoadBalancerResponseEvent response = new ApplicationLoadBalancerResponseEvent();
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");
        response.setHeaders(headers);
        response.setIsBase64Encoded(false);

        try {
            // Route based on HTTP method and path
            String path = input.getPath();
            String httpMethod = input.getHttpMethod();

            if ("POST".equals(httpMethod) && "/users".equals(path)) {
                return createUser(input, context);
            } else {
                return buildResponse(404, "{\"error\": \"Not Found\"}");
            }

        } catch (Exception e) {
            context.getLogger().log("Error: " + e.getMessage());
            return buildResponse(500, "{\"error\": \"" + e.getMessage() + "\"}");
        }
    }

    /**
     * Create a new user in Cognito User Pool
     */
    private ApplicationLoadBalancerResponseEvent createUser(ApplicationLoadBalancerRequestEvent input,
            Context context) {
        try {
            // Parse request body
            Map<String, String> requestBody = objectMapper.readValue(input.getBody(), Map.class);

            String username = requestBody.get("username");
            String email = requestBody.get("email");
            String phoneNumber = requestBody.get("phoneNumber");

            if (username == null || username.isEmpty()) {
                return buildResponse(400, "{\"error\": \"Username is required\"}");
            }

            // Build user attributes
            AdminCreateUserRequest.Builder requestBuilder = AdminCreateUserRequest.builder()
                    .userPoolId(userPoolId)
                    .username(username)
                    .temporaryPassword(requestBody.getOrDefault("temporaryPassword", "TempPass123!"));

            // Add optional attributes
            if (email != null && !email.isEmpty()) {
                requestBuilder.userAttributes(
                        AttributeType.builder().name("email").value(email).build(),
                        AttributeType.builder().name("email_verified").value("true").build());
            }

            if (phoneNumber != null && !phoneNumber.isEmpty()) {
                requestBuilder.userAttributes(
                        AttributeType.builder().name("phone_number").value(phoneNumber).build());
            }

            // Call Cognito API
            AdminCreateUserResponse cognitoResponse = cognitoIdentityProviderClient
                    .adminCreateUser(requestBuilder.build());

            context.getLogger().log("User created: " + cognitoResponse.user().username());

            // Build success response
            Map<String, Object> responseBody = new HashMap<>();
            responseBody.put("message", "User created successfully");
            responseBody.put("username", cognitoResponse.user().username());
            responseBody.put("status", cognitoResponse.user().userStatusAsString());

            String jsonResponse = objectMapper.writeValueAsString(responseBody);
            return buildResponse(201, jsonResponse);

        } catch (CognitoIdentityProviderException e) {
            context.getLogger().log("Cognito error: " + e.awsErrorDetails().errorMessage());
            return buildResponse(400, "{\"error\": \"" + e.awsErrorDetails().errorMessage() + "\"}");
        } catch (Exception e) {
            context.getLogger().log("Error creating user: " + e.getMessage());
            return buildResponse(500, "{\"error\": \"Internal server error\"}");
        }
    }

    /**
     * Helper method to build ALB response
     */
    private ApplicationLoadBalancerResponseEvent buildResponse(int statusCode, String body) {
        ApplicationLoadBalancerResponseEvent response = new ApplicationLoadBalancerResponseEvent();
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");
        response.setHeaders(headers);
        response.setStatusCode(statusCode);
        response.setBody(body);
        response.setIsBase64Encoded(false);
        return response;
    }
}
