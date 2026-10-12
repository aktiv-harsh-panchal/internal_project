FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies required by Odoo
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libldap2-dev \
    libsasl2-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libssl-dev \
    libffi-dev \
    libyaml-dev \
    node-less \
    npm \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Create Odoo user
RUN useradd --create-home --shell /bin/bash odoo

WORKDIR /opt/odoo

# Clone the exact Odoo source currently used by the host
RUN git clone https://github.com/odoo/odoo.git . \
    && git checkout 6fc51dd2bdca9f189247c9fc9f7a12776babb72b

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Create directories used by Odoo
RUN mkdir -p /var/lib/odoo /mnt/custom-addons \
    && chown -R odoo:odoo /opt/odoo /var/lib/odoo /mnt/custom-addons

USER odoo

EXPOSE 8069 8072

CMD ["python3", "odoo-bin", "-c", "/etc/odoo/odoo.conf"]
