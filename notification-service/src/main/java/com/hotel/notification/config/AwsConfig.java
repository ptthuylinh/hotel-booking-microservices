package com.hotel.notification.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.sqs.SqsClient;

@Configuration
public class AwsConfig {

    private static final Logger log = LoggerFactory.getLogger(AwsConfig.class);

    @Value("${aws.region:us-east-1}")
    private String awsRegion;

    @Bean
    public SqsClient sqsClient() {
        try {
            return SqsClient.builder()
                    .region(Region.of(awsRegion))
                    .credentialsProvider(DefaultCredentialsProvider.create())
                    .build();
        } catch (Exception e) {
            log.warn("Không thể khởi tạo SqsClient với default credentials: {}", e.getMessage());
            return SqsClient.builder()
                    .region(Region.of(awsRegion))
                    .build();
        }
    }
}
