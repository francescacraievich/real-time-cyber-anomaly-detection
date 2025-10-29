
# Formatting logs to create an homogeneous dataframe

## Columns that are in common

-   timestamp - Present in all 4 dataframes, essential for temporal correlation
-   src_ip / src_hostname - Source IP addresses (DF1, DF2, DF3 have src_ip; DF2 also has src_hostname)
-   dst_ip / dest_ip - Destination IP (DF1, DF2, DF3 use different naming)
-   src_port - Source port (DF1, DF2, DF3)
-   dst_port / dest_port - Destination port (DF1, DF2, DF3)

-   OSS: DF4 does not have the src/dst port 

### IDEA: discard very specific columns for each dataframe

SSH-specific fingerprinting (keep only if doing SSH analysis):

- hassh, hasshAlgorithms, kexAlgs, keyAlgs, encCS, macCS, compCS, langCS
version (SSH version)

Low-level network details:

- flow_id, in_iface, pkt_src, direction, flow, stream, tx_id (Suricata)
icmp_type, icmp_code, response_icmp_type, response_icmp_code (unless ICMP-focused)

File/payload details (discard for overview, keep for deep analysis):

- ttylog, arch, size, shasum, duplicate, data, id (Cowrie)
payload, payload_printable (Suricata)
headers, cookies, post_data (Tanner)

Protocol-specific nested data (unless analyzing specific protocols):

- tls, http, fileinfo, tcp, smb, sip, files, ssh, tftp, snmp, rfb, pgsql, smtp (Suricata  these are nested JSON/dicts)
ftp (Dionaea - likely nested)

Ambiguous/low-value:

- anomaly, tx_guessed, app_proto_tc, app_proto_orig, app_proto_ts (Suricata)
src_hostname (Dionaea - often null or unreliable)
duration (Cowrie - unless analyzing session lengths)
metadata (Suricata - often empty)
uuid, peer (Tanner - internal references) 