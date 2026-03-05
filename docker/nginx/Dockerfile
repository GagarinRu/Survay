FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY ./configs/site.conf /etc/nginx/site.conf.template
COPY generate_config.sh /generate_config.sh

RUN chmod +x /generate_config.sh

CMD ["/generate_config.sh"]