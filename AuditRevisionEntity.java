package com.intelligence.audit;

import lombok.Data;
import org.hibernate.envers.DefaultRevisionEntity;
import org.hibernate.envers.RevisionEntity;
import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "revinfo_extended")
@RevisionEntity(AuditRevisionListener.class)
@Data
public class AuditRevisionEntity extends DefaultRevisionEntity {
    
    // This stores the hash provided by the Python crawler
    private String dataHash;
    
    // This stores the crawler build/version number
    private String crawlerBuild;
}