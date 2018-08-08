CREATE TABLE bijis (
    filepath    text        PRIMARY KEY COLLATE NOCASE,
    filename    text        NOT NULL,
    suffix      text        NOT NULL,
    mimetype    text,
    filesize    integer     NOT NULL,
    updatedAt   text        NOT NULL,
    backupAt    text        NOT NULL,
    bijiCTime   text        NOT NULL,
    bijiMTime   text        NOT NULL check(bijiMTime <> '')
);

CREATE INDEX bijis_filename_idx ON bijis(filename);
CREATE INDEX bijis_updatedAt_idx ON bijis(updatedAt);
CREATE INDEX bijis_backupAt_idx ON bijis(backupAt);
CREATE INDEX bijis_bijiCTime_idx ON bijis(bijiCTime);
CREATE INDEX bijis_bijiMTime_idx ON bijis(bijiMTime);

CREATE TABLE tags (
    tag         text        PRIMARY KEY,
    usedAt      text        NOT NULL check(usedAt <> '')
);

CREATE INDEX tags_usedAt ON tags(usedat);

CREATE TABLE tag_biji (
    tag         text        REFERENCES tags(tag)
                            ON UPDATE CASCADE
                            ON DELETE CASCADE,
    filepath    text        REFERENCES bijis(filepath)
                            ON UPDATE CASCADE
                            ON DELETE CASCADE
);
