
# Formatting logs to create an homogeneous dataframe

## view of the columns for all 4 dataframes
- Cowrie Columns: Index(['eventid', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'session',
       'protocol', 'message', 'sensor', 'timestamp', 'duration', 'version',
       'hassh', 'hasshAlgorithms', 'kexAlgs', 'keyAlgs', 'encCS', 'macCS',
       'compCS', 'langCS', 'username', 'password', 'arch', 'input', 'ttylog',
       'size', 'shasum', 'duplicate', 'data', 'id'],
      dtype='object')

- Dionea Columns: Index(['connection', 'dst_ip', 'dst_port', 'src_hostname', 'src_ip',
       'src_port', 'timestamp', 'ftp', 'credentials'],
      dtype='object')
      
- Suricata Columns: Index(['timestamp', 'flow_id', 'in_iface', 'event_type', 'src_ip', 'dest_ip',
       'proto', 'icmp_type', 'icmp_code', 'pkt_src', 'alert', 'direction',
       'flow', 'payload', 'payload_printable', 'stream', 'src_port',
       'dest_port', 'app_proto', 'metadata', 'tls', 'tx_id', 'http',
       'fileinfo', 'tcp', 'smb', 'response_icmp_type', 'response_icmp_code',
       'sip', 'files', 'app_proto_tc', 'anomaly', 'ssh', 'tftp', 'tx_guessed',
       'app_proto_orig', 'snmp', 'rfb', 'app_proto_ts', 'pgsql', 'smtp'],
      dtype='object')

- Tanner Columns: Index(['method', 'path', 'headers', 'uuid', 'peer', 'status', 'cookies',
       'response_msg', 'timestamp', 'post_data'],
      dtype='object')

## After the formatting
- Cowrie Columns: Index(['eventid', 'source_ip', 'session', 'message', 'sensor', 'event_time'], dtype='object')  
- Dionea Columns: Index(['connection', 'destination_ip', 'destination_port', 'src_hostname',
       'source_ip', 'source_port', 'event_time'],
      dtype='object')
- Suricata Columns: Index(['event_time', 'flow_id', 'in_iface', 'event_type', 'source_ip',
       'destination_ip', 'proto', 'pkt_src', 'flow', 'source_port',
       'destination_port'],
      dtype='object')

## Columns that are in common

-   timestamp - Present in all 4 dataframes, essential for temporal correlation
-   src_ip / src_hostname - Source IP addresses (DF1, DF2, DF3 have src_ip; DF2 also has src_hostname)
-   dst_ip / dest_ip - Destination IP (DF1, DF2, DF3 use different naming)
-   src_port - Source port (DF1, DF2, DF3)
-   dst_port / dest_port - Destination port (DF1, DF2, DF3)

-   OSS: DF4 does not have the src/dst port (they are in the peer column)

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


### Questions
- why do we have different src_ip for all the various attacks across all 4 dataframes?
- Maybe do not use the dataframe obtained from the Tanner honeypot
    - low amount of rows in respect to others 
- Idea that i have: format the columns that are in common so that the df can be merged on them
- we should discuss what are the events we want to identify (like deciding on what protocols to focus on the analisys)
- "peer" column in Tanner constains what? (src or dst?)

## responses
- Tunner not used
- Different IP probably beacuse of the different Honeypots
- Unite all dataframes
- col with > 50% NaN must be eliminated (currently i have a mask that keeps all the cols with less that 80% values missing)
- Need event to analyze

# Recap
- need to reformat the class df_formatter for all 4 dataframes sparately and 1 class for uniting all the dataframes

