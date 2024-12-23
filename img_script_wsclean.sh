wsclean \
    -size 2048 2048 \
    -scale 1.4asec \
    -weight briggs 0.0 \
    -multiscale \
    -niter 30000 \
    -mgain 0.7 \
    -data-column CORRECTED_DATA \
    -pol xx \
    -auto-mask 3 \
    -auto-threshold 0.3 \
    -local-rms \
    -spws 11,12,13,14,15,16,17,18,19,20 \
    -intervals-out 1 \
    -name eovsa111 \
    /Users/peijinz/eovsa_im/UDB20241212_merged.ms