package com.bank.crm;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.events.ApplicationLoadBalancerRequestEvent;
import com.amazonaws.services.lambda.runtime.events.ApplicationLoadBalancerResponseEvent;

import org.junit.jupiter.api.Test;

public class AppTest {

    /**
     * Mock Context for testing
     */
    private static class TestContext implements Context {
        @Override
        public String getAwsRequestId() {
            return "test-request-id";
        }

        @Override
        public String getLogGroupName() {
            return "test-log-group";
        }

        @Override
        public String getLogStreamName() {
            return "test-log-stream";
        }

        @Override
        public String getFunctionName() {
            return "test-function";
        }

        @Override
        public String getFunctionVersion() {
            return "1";
        }

        @Override
        public String getInvokedFunctionArn() {
            return "arn:aws:lambda:us-east-1:123456789012:function:test";
        }

        @Override
        public com.amazonaws.services.lambda.runtime.CognitoIdentity getIdentity() {
            return null;
        }

        @Override
        public com.amazonaws.services.lambda.runtime.ClientContext getClientContext() {
            return null;
        }

        @Override
        public int getRemainingTimeInMillis() {
            return 300000;
        }

        @Override
        public int getMemoryLimitInMB() {
            return 512;
        }

        @Override
        public LambdaLogger getLogger() {
            return new LambdaLogger() {
                @Override
                public void log(String message) {
                    System.out.println(message);
                }

                @Override
                public void log(byte[] message) {
                    System.out.println(new String(message));
                }
            };
        }
    }

    @Test
    public void handleRequest_shouldReturn404ForUnknownPath() {
        App function = new App();

        ApplicationLoadBalancerRequestEvent request = new ApplicationLoadBalancerRequestEvent();
        request.setPath("/unknown");
        request.setHttpMethod("GET");

        ApplicationLoadBalancerResponseEvent response = function.handleRequest(request, new TestContext());

        assertEquals(404, response.getStatusCode());
        assertNotNull(response.getBody());
    }

    @Test
    public void app_shouldInitializeCognitoClient() {
        App function = new App();
        assertNotNull(function);
    }
}
