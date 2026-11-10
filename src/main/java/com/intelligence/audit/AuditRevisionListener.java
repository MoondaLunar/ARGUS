package com.intelligence.audit;

import org.hibernate.envers.RevisionListener;
import com.intelligence.context.AuditContext;

public class AuditRevisionListener implements RevisionListener {

    @Override
    public void newRevision(Object revisionEntity) {
        AuditRevisionEntity rev = (AuditRevisionEntity) revisionEntity;
        // Pulling data from the current request thread context
        rev.setDataHash(AuditContext.getDataHash());
        rev.setCrawlerBuild(AuditContext.getBuildNumber());
    }
}