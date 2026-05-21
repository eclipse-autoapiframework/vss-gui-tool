#!/usr/bin/env sh
set -eu

# This script is intended to be run inside the dev container to prepare the workspace by downloading the CA bundle and updating the system trust store.
# Uncomment the following lines if you need to download the CA bundle and update the trust store when the container starts.

#CA_BUNDLE_URL=https://your-server/cabundle.crt
 

if [ -n "${CA_BUNDLE_URL:-}" ]; then
	echo "[INFO] Downloading CA bundle from ${CA_BUNDLE_URL} and updating system trust store..."
	wget "${CA_BUNDLE_URL}" -O /tmp/cabundle.crt --no-check-certificate
	awk 'split_after == 1 {n++;split_after=0} /-----END CERTIFICATE-----/ {split_after=1} {print > "/usr/local/share/ca-certificates/cert" n ".crt"}' < /tmp/cabundle.crt
	rm -f /tmp/cabundle.crt
	update-ca-certificates
fi
