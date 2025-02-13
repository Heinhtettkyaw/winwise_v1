// spring-boot-service/src/main/java/com/example/demo/util/MultipartInputStreamFileResource.java
package com.example.demo.util;

import java.io.IOException;
import java.io.InputStream;
import org.springframework.core.io.InputStreamResource;

public class MultipartInputStreamFileResource extends InputStreamResource {

    private final String filename;

    public MultipartInputStreamFileResource(InputStream inputStream, String filename) {
        super(inputStream);
        this.filename = filename;
    }

    @Override
    public String getFilename() {
        return this.filename;
    }

    @Override
    public long contentLength() throws IOException {
        return -1; // content length is not specified
    }
}
