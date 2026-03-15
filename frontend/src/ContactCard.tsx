import React from 'react';

interface Props {
  contact: {
    id: string;
    name: string;
    mobile: string;
  };
}

const ContactCard: React.FC<Props> = ({ contact }) => {
  return (
    <div>
      <h3>{contact.name}</h3>
      <p>{contact.mobile}</p>
    </div>
  );
};

export default ContactCard;