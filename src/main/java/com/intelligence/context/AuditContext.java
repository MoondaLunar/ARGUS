package com.intelligence.context;

public class AuditContext {
    private static final ThreadLocal<String> BUILD_NUMBER = new ThreadLocal<>();
    private static final ThreadLocal<String> DATA_HASH = new ThreadLocal<>();

    public static void set(String build, String hash) {
        BUILD_NUMBER.set(build);
        DATA_HASH.set(hash);
    }

    public static String getBuildNumber() {
        return BUILD_NUMBER.get();
    }

    public static String getDataHash() {
        return DATA_HASH.get();
    }

    public static void clear() {
        BUILD_NUMBER.remove();
        DATA_HASH.remove();
    }
}