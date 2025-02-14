package com.example.demo.controller;

import com.example.demo.util.MultipartInputStreamFileResource;
import java.io.IOException;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api")
public class FileUploadController {

    private final RestTemplate restTemplate = new RestTemplate();

    // URL of the Python ML service
    private final String pythonServiceUrl = "http://localhost:5000/train";

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> handleFileUpload(
            @RequestParam("league") String league,
            @RequestParam("file2") MultipartFile file2, // current standings
            @RequestParam("file3") MultipartFile file3  // remaining fixtures
    ) throws IOException {

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("league", league);
        body.add("file2", new MultipartInputStreamFileResource(file2.getInputStream(), file2.getOriginalFilename()));
        body.add("file3", new MultipartInputStreamFileResource(file3.getInputStream(), file3.getOriginalFilename()));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        ResponseEntity<String> response = restTemplate.postForEntity(pythonServiceUrl, requestEntity, String.class);
        return ResponseEntity.ok(response.getBody());
    }
}
